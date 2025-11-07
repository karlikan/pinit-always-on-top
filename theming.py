from PySide6.QtCore import Qt, QEasingCurve, QVariantAnimation
from PySide6.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect

LIGHT = {
    "bg": "#FFFFFF",
    "surface": "#F5F5F7",
    "text": "#111111",
    "muted": "#666666",
    "accent": "#2D74FF",
    "border": "#E6E6EA",
}

DARK = {
    "bg": "#121212",
    "surface": "#1C1C1F",
    "text": "#EDEDED",
    "muted": "#ADADAD",
    "accent": "#4B8DFF",
    "border": "#2A2A2E",
}

def build_styles(colors: dict) -> str:
    return f"""
        QWidget {{
            background-color: {colors['bg']};
            color: {colors['text']};
            font-family: "Segoe UI", system-ui, -apple-system, "Inter", Arial;
            font-size: 13px;
        }}
        QLineEdit, QListWidget, QTextEdit, QPlainTextEdit {{
            background: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 10px;
            padding: 8px 10px;
            selection-background-color: {colors['accent']};
        }}
        QPushButton {{
            background: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 12px;
            padding: 8px 14px;
        }}
        QPushButton:hover {{ border-color: {colors['accent']}; }}
        QPushButton:pressed {{ background: {colors['bg']}; }}
        #PrimaryButton {{ background: {colors['accent']}; color: white; border: none; }}
        #Header {{ background: {colors['surface']}; border-bottom: 1px solid {colors['border']}; }}
        #Footer {{ background: {colors['surface']}; border-top: 1px solid {colors['border']}; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px; }}
        QScrollBar::handle:vertical {{ background: {colors['border']}; border-radius: 5px; min-height: 40px; }}
    """

class ThemeManager:
    def __init__(self, root: QWidget, start_dark: bool = False):
        self.root = root
        self.dark = start_dark
        self.apply_immediate()

    def palette_colors(self):
        return DARK if self.dark else LIGHT

    def apply_immediate(self):
        self.root.setStyleSheet(build_styles(self.palette_colors()))

    def set_dark(self, value: bool):
        if value == self.dark:
            return
        # Снимок и плавный фейд
        pix = self.root.grab()
        overlay = QLabel(self.root)
        overlay.setPixmap(pix)
        overlay.setGeometry(0, 0, self.root.width(), self.root.height())
        effect = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(effect)
        overlay.show()

        self.dark = value
        self.apply_immediate()

        anim = QVariantAnimation(self.root)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setDuration(280)
        anim.valueChanged.connect(lambda v: effect.setOpacity(v))
        anim.finished.connect(lambda: (overlay.hide(), overlay.deleteLater()))
        anim.start()
