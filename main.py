import sys, os, json
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QLabel,
    QDialog, QFormLayout, QComboBox
)
import winpin
from theming import ThemeManager

APP_NAME = "PinIt — Always on Top"
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"dark": False}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

class PickerOverlay(QWidget):
    def __init__(self, parent=None, on_pick=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.on_pick = on_pick
        self.label = QLabel("Клик по окну — закрепить/снять (ПКМ — отмена)", self)
        self.label.setStyleSheet("color: white; background: rgba(0,0,0,128); padding: 12px 16px; border-radius: 12px;")
        self.label.adjustSize()

    def showFull(self):
        g = QApplication.primaryScreen().geometry()
        self.setGeometry(g)
        self.label.move(self.width()//2 - self.label.width()//2, 40)
        self.show()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            gp = self.mapToGlobal(e.position().toPoint())
            hwnd = winpin.hwnd_from_point(gp.x(), gp.y())
            if hwnd:
                now = winpin.is_topmost(hwnd)
                winpin.set_topmost(hwnd, not now)
            if self.on_pick:
                self.on_pick(hwnd)
            self.close()
        elif e.button() == Qt.RightButton:
            self.close()

class SettingsDialog(QDialog):
    def __init__(self, theme: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.setMinimumWidth(360)
        l = QVBoxLayout(self)
        form = QFormLayout()
        self.combo = QComboBox()
        self.combo.addItems(["Светлая", "Тёмная"])
        self.combo.setCurrentIndex(1 if self.theme.dark else 0)
        form.addRow("Тема:", self.combo)
        l.addLayout(form)
        row = QHBoxLayout()
        ok = QPushButton("Сохранить"); ok.setObjectName("PrimaryButton")
        cancel = QPushButton("Отмена")
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        row.addStretch(1); row.addWidget(cancel); row.addWidget(ok)
        l.addLayout(row)
    def apply_changes(self):
        self.theme.set_dark(self.combo.currentIndex() == 1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(720, 480)
        self.cfg = load_config()
        self.theme = ThemeManager(self, start_dark=self.cfg.get("dark", False))

        root = QWidget(); self.setCentralWidget(root)
        main = QVBoxLayout(root); main.setContentsMargins(14,14,14,14); main.setSpacing(12)

        header = QWidget(); header.setObjectName("Header")
        h = QHBoxLayout(header); h.setContentsMargins(12,10,12,10)
        title = QLabel("📌 PinIt"); title.setStyleSheet("font-weight:600; font-size:16px;")
        gear = QPushButton("⚙"); gear.setFixedSize(36,32); gear.setToolTip("Настройки"); gear.clicked.connect(self.open_settings)
        h.addWidget(title); h.addStretch(1); h.addWidget(gear); main.addWidget(header)

        controls = QHBoxLayout()
        self.pin_active_btn = QPushButton("Закрепить активное"); self.pin_active_btn.setObjectName("PrimaryButton")
        self.pin_active_btn.clicked.connect(self.pin_active)
        self.pick_btn = QPushButton("Пикер окна"); self.pick_btn.clicked.connect(self.pick_window)
        self.unpin_all_btn = QPushButton("Снять все закрепления"); self.unpin_all_btn.clicked.connect(self.unpin_all)
        controls.addWidget(self.pin_active_btn); controls.addWidget(self.pick_btn); controls.addWidget(self.unpin_all_btn); controls.addStretch(1)
        main.addLayout(controls)

        sr = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Поиск окна по заголовку…"); self.search.textChanged.connect(self.refresh_list)
        refresh = QPushButton("Обновить"); refresh.clicked.connect(self.refresh_list)
        sr.addWidget(self.search,1); sr.addWidget(refresh); main.addLayout(sr)

        self.list = QListWidget(); self.list.itemDoubleClicked.connect(self.toggle_item_pin); main.addWidget(self.list,1)

        footer = QWidget(); footer.setObjectName("Footer")
        f = QHBoxLayout(footer); f.setContentsMargins(12,8,12,8)
        self.status = QLabel("Готово"); self.status.setStyleSheet("color:#888;")
        tip = QLabel("Двойной клик — закрепить/снять"); tip.setStyleSheet("color:#888;")
        f.addWidget(self.status); f.addStretch(1); f.addWidget(tip); main.addWidget(footer)

        self.pinned = set()
        self.refresh_list()

    def closeEvent(self, e):
        self.cfg["dark"] = self.theme.dark; save_config(self.cfg)
        return super().closeEvent(e)

    def set_status(self, text):
        self.status.setText(text)
        QTimer.singleShot(2500, lambda: self.status.setText("Готово"))

    def open_settings(self):
        dlg = SettingsDialog(self.theme, self)
        if dlg.exec():
            dlg.apply_changes()
            self.cfg["dark"] = self.theme.dark; save_config(self.cfg)

    def refresh_list(self, *_a, select_hwnd=None):
        query = self.search.text().strip().lower()
        items = winpin.enum_windows()
        self.list.clear()
        for w in items:
            title = w["title"]; cls = w["cls"]; hwnd = w["hwnd"]
            if query and query not in title.lower():
                continue
            mark = "📌 " if winpin.is_topmost(hwnd) else ""
            it = QListWidgetItem(f"{mark}{title}  —  [{cls}]  (hwnd {hwnd})")
            it.setData(Qt.UserRole, hwnd)
            self.list.addItem(it)
            if select_hwnd and hwnd == select_hwnd:
                self.list.setCurrentItem(it)

    def toggle_item_pin(self, item: QListWidgetItem):
        hwnd = item.data(Qt.UserRole); 
        if not hwnd: return
        now = winpin.is_topmost(hwnd)
        winpin.set_topmost(hwnd, not now)
        if winpin.is_topmost(hwnd): self.pinned.add(hwnd)
        else: self.pinned.discard(hwnd)
        self.refresh_list(select_hwnd=hwnd)

    def pin_active(self):
        hwnd = winpin.get_foreground()
        if not hwnd:
            self.set_status("Нет активного окна"); return
        now = winpin.is_topmost(hwnd)
        winpin.set_topmost(hwnd, not now)
        if winpin.is_topmost(hwnd): self.pinned.add(hwnd); self.set_status("Окно закреплено")
        else: self.pinned.discard(hwnd); self.set_status("Закрепление снято")
        self.refresh_list(select_hwnd=hwnd)

    def pick_window(self):
        self.set_status("Режим пикера: ЛКМ — выбрать, ПКМ — отмена")
        ov = PickerOverlay(on_pick=lambda hwnd: self.after_pick(hwnd))
        ov.showFull()

    def after_pick(self, hwnd):
        if hwnd:
            if winpin.is_topmost(hwnd): self.pinned.add(hwnd); self.set_status("Окно закреплено")
            else: self.pinned.discard(hwnd); self.set_status("Закрепление снято")
            self.refresh_list(select_hwnd=hwnd)
        else:
            self.set_status("Не удалось определить окно")

    def unpin_all(self):
        for hwnd in list(self.pinned):
            if winpin.is_topmost(hwnd): winpin.set_topmost(hwnd, False)
        self.pinned.clear(); self.set_status("Сняты все закрепления"); self.refresh_list()

def main():
    app = QApplication(sys.argv)
    w = MainWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
