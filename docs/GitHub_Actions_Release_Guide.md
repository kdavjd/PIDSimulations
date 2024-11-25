# Руководство по релизам PyQt приложений через GitHub Actions

## Содержание
- [Процесс релиза и его этапы](#процесс-релиза-и-его-этапы)
- [Пайплайн сборки релиза](#пайплайн-сборки-релиза)
- [Особенности GitHub Actions](#особенности-github-actions)
- [Работа с PyQt в релизах](#работа-с-pyqt-в-релизах)
- [PyQt и PyInstaller](#pyqt-и-pyinstaller)

## Процесс релиза и его этапы

Процесс релиза PyQt приложения через GitHub Actions состоит из следующих взаимосвязанных этапов:

1. **Подготовка кода**
   - Обновление версии в метаданных
   - Проверка зависимостей
   - Создание тега версии
   
2. **Тестирование**
   - Запуск unit-тестов
   - Проверка линтером
   - Тестирование сборки

3. **Сборка**
   - Подготовка окружения
   - Установка зависимостей
   - Компиляция ресурсов PyQt
   - Создание исполняемого файла

4. **Публикация**
   - Создание GitHub Release
   - Загрузка артефактов
   - Обновление документации

## Пайплайн сборки релиза

Ниже представлен подробный пайплайн для GitHub Actions:

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10']

    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install PyInstaller
        
    - name: Install PyQt
      run: |
        pip install PyQt6
        
    - name: Build with PyInstaller
      run: |
        pyinstaller --onefile --windowed --name myapp src/main.py
        
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: myapp-${{ matrix.os }}
        path: dist/*
```

### Анализ каждого шага

#### 1. Триггер workflow
- **Цель**: Запуск сборки при создании git-тега, начинающегося с 'v'
- **Потенциальные ошибки**: 
  - Неправильный формат тега
  - Отсутствие прав на создание релиза
- **Решение**: Использовать семантическое версионирование (v1.0.0)
- **Документация**: [Workflow triggers](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow)

#### 2. Настройка матрицы сборки
- **Цель**: Обеспечение кросс-платформенной сборки
- **Зависимости**: Нет
- **Потенциальные ошибки**: 
  - Несовместимость версий Python
  - Различия в путях между ОС
- **Документация**: [Using a build matrix](https://docs.github.com/en/actions/using-jobs/using-a-build-matrix)

#### 3. Установка зависимостей
- **Цель**: Подготовка окружения для сборки
- **Зависимости**: Успешный checkout и setup-python
- **Потенциальные ошибки**:
  - Конфликты версий пакетов
  - Отсутствие системных зависимостей
- **Решение**: 
  - Фиксация версий в requirements.txt
  - Добавление системных зависимостей через apt/brew
- **Документация**: [Installing dependencies](https://docs.github.com/en/actions/guides/building-and-testing-python)

## Особенности GitHub Actions

1. **Кэширование**
   - Кэширование pip и зависимостей ускоряет сборку
   - [Документация по кэшированию](https://docs.github.com/en/actions/using-workflows/caching-dependencies)

2. **Секреты**
   - Хранение конфиденциальных данных
   - [Управление секретами](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

3. **Артефакты**
   - Ограничение времени хранения
   - Лимиты размера
   - [Работа с артефактами](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)

## Работа с PyQt в релизах

### Особенности установки PyQt:

1. **Системные зависимости**
   - Windows: Не требуются дополнительные действия
   - Linux: Требуется установка X11 библиотек
   - macOS: Может потребоваться установка дополнительных фреймворков

2. **Версионирование**
   - PyQt5 vs PyQt6
   - Совместимость с Python
   - [Stack Overflow: PyQt versions](https://stackoverflow.com/questions/tagged/pyqt)

### Рекомендации:

```yaml
- name: Install Linux dependencies
  if: runner.os == 'Linux'
  run: |
    sudo apt-get update
    sudo apt-get install -y libxcb-xinerama0
    sudo apt-get install -y libxkbcommon-x11-0
    sudo apt-get install -y libxcb-icccm4
```

## PyQt и PyInstaller

### Проблемы совместимости:

1. **Missing Modules**
   - Причина: PyInstaller не всегда определяет все зависимости PyQt
   - Решение: Явное указание hidden imports
   - [Stack Overflow: PyInstaller missing modules](https://stackoverflow.com/questions/tagged/pyinstaller+pyqt)

2. **Ресурсы и плагины**
   - QML файлы
   - Изображения и иконки
   - Плагины Qt

### Пример spec-файла:

```python
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources')],
    hiddenimports=['PyQt6.QtPrintSupport'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
```

### Решение проблем:

1. **Отсутствие DLL**
   - Использование --add-binary
   - [PyInstaller Manual](https://pyinstaller.org/en/stable/usage.html)

2. **Конфликты версий**
   - Изоляция окружения
   - Точное указание версий в requirements.txt

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyQt Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Stack Overflow - PyQt](https://stackoverflow.com/questions/tagged/pyqt)
- [Stack Overflow - PyInstaller](https://stackoverflow.com/questions/tagged/pyinstaller)

## Полезные ссылки по разделам

#### Процесс релиза
- [Автоматизация версионирования в Python проектах](https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package)
- [Создание GitHub Release через Actions](https://stackoverflow.com/questions/63932728/how-to-create-a-github-release-using-github-actions)
- [Автоматическое обновление CHANGELOG](https://stackoverflow.com/questions/40909584/how-to-automatically-generate-changelog-using-github-release-notes)

#### GitHub Actions
- [Матрица сборки для разных OS](https://stackoverflow.com/questions/57806624/github-actions-how-to-build-different-branches-for-different-operating-systems)
- [Кэширование pip зависимостей](https://stackoverflow.com/questions/58176116/github-actions-how-to-cache-pip-dependencies)
- [Управление секретами в workflow](https://stackoverflow.com/questions/53648244/how-to-use-environment-variables-in-github-actions)

#### PyQt установка и сборка
- [Решение проблем с X11 на Linux](https://stackoverflow.com/questions/44389883/pyqt-on-linux-without-display-x-server)
- [Установка PyQt6 в CI/CD](https://stackoverflow.com/questions/69515086/install-pyqt6-in-github-actions-workflow)
- [Сборка QML ресурсов](https://stackoverflow.com/questions/66799067/how-to-package-a-pyqt-qml-application-with-pyinstaller)

#### PyInstaller специфика
- [Добавление скрытых импортов PyQt](https://stackoverflow.com/questions/63859101/pyinstaller-cant-find-the-qt-plugins-directory-after-packaging)
- [Решение проблем с DLL](https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile)
- [Включение ресурсов в сборку](https://stackoverflow.com/questions/51060894/adding-data-files-in-pyinstaller-using-spec-file)

#### Тестирование PyQt приложений
- [Настройка QTest в CI](https://stackoverflow.com/questions/55432331/qt-testing-in-ci-pipeline)
- [Мокирование PyQt виджетов](https://stackoverflow.com/questions/56577107/how-to-mock-pyqt-widgets-in-unit-tests)
- [Тестирование GUI без дисплея](https://stackoverflow.com/questions/18291631/how-to-run-pyqt-applications-without-a-display)

#### Решение частых проблем
- [Отсутствие Qt плагинов в сборке](https://stackoverflow.com/questions/62055625/missing-qt-platform-plugin-when-running-pyinstaller-built-exe)
- [Проблемы с путями в PyInstaller](https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile)
- [Ошибки импорта PyQt модулей](https://stackoverflow.com/questions/56202784/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-windows-in-even-though-it)

#### Оптимизация workflow
- [Параллельные задачи в GitHub Actions](https://stackoverflow.com/questions/57711558/how-to-run-multiple-jobs-in-parallel-in-github-actions)
- [Условное выполнение шагов](https://stackoverflow.com/questions/58139406/only-run-job-on-specific-branch-with-github-actions)
- [Оптимизация времени сборки](https://stackoverflow.com/questions/55454032/how-to-optimize-gradle-build-time-in-github-actions)

#### Дополнительные ресурсы
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt Documentation](https://doc.qt.io/)
