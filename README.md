# PinIt — Always on Top (Windows 10/11)

Минималистичное **portable**‑приложение для закрепления любых окон поверх остальных.

## Основное
- Pin активного окна
- Выбор окна из списка
- Пикер окна (клик по любому окну)
- Светлая/тёмная тема с плавным фейдом
- Ресайз окна, современный UI
- Portable (без установки): `dist/PinIt/PinIt.exe`

## Быстрая сборка онлайн (GitHub Actions)
1. Создай публичный репозиторий и **загрузи все файлы этого архива**.
2. Зайди во вкладку **Actions** → **Build Windows Portable** → **Run workflow**.
3. Скачай артефакт **PinIt-portable.zip**.

## Запуск из исходников (локально)
```powershell
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt
py -3 main.py
```

## Локальная сборка portable
```powershell
py -3 -m pip install pyinstaller
py -3 -m PyInstaller --noconfirm --clean `
  --name "PinIt" `
  --windowed `
  --onedir `
  --add-data "assets;assets" `
  main.py
```
Готовый exe: `dist/PinIt/PinIt.exe`.

## Примечания
- Для окон, запущенных **от администратора**, запускай PinIt тоже **от администратора**.
- SmartScreen может предупреждать про неизвестного издателя — это нормально для самосборов.
