import logging
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from core.simulatons import log_exceptions

CANVAS_BIG_SIZE = 12
CANVAS_MEDIUM_SIZE = 10
CANVAS_SMALL_SIZE = 8


class PlotCanvas(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger("PIDSimulationsLogger")

        # Настройка стиля matplotlib
        plt.style.use(["seaborn-v0_8-darkgrid"])  # Используем встроенный стиль вместо science
        plt.rc("font", size=CANVAS_MEDIUM_SIZE)  # Основной размер шрифта
        plt.rc("axes", titlesize=CANVAS_BIG_SIZE)  # Размер шрифта заголовков осей
        plt.rc("axes", labelsize=CANVAS_MEDIUM_SIZE)  # Размер шрифта меток осей
        plt.rc("xtick", labelsize=CANVAS_SMALL_SIZE)  # Размер шрифта меток по оси X
        plt.rc("ytick", labelsize=CANVAS_SMALL_SIZE)  # Размер шрифта меток по оси Y
        plt.rc("legend", fontsize=CANVAS_SMALL_SIZE)  # Размер шрифта легенды
        plt.rc("figure", titlesize=CANVAS_BIG_SIZE)  # Размер шрифта заголовка фигуры

        # Создание фигуры matplotlib и холста
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)  # Добавляем начальную область для графика

        # Панель инструментов для холста
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Словарь для хранения линий графиков по именам
        self.lines: dict[str, Line2D] = {}

        # Настройка компоновки для PlotCanvas
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Добавляем панель инструментов сверху
        layout.addWidget(self.canvas)  # Добавляем холст под панелью инструментов
        self.setLayout(layout)

    @pyqtSlot(dict)
    @log_exceptions
    def plot_data(self, params: dict):
        x = params.get("x")
        y = params.get("y")
        label = params.get("label")
        self.logger.debug(f"Plotting data with label: {label}")
        self.logger.debug(f"x shape: {len(x)}, y shape: {len(y)}")

        if label in self.lines:
            # Обновляем данные существующей линии
            self.logger.debug("Updating existing line")
            self.lines[label].set_data(x, y)
        else:
            # Создаем новую линию
            self.logger.debug("Creating new line")
            (line,) = self.axes.plot(x, y, label=label)
            self.lines[label] = line

        # Добавляем подписи осей
        self.axes.set_xlabel("Время (с)")
        self.axes.set_ylabel("Температура (°C)")

        self.axes.relim()
        self.axes.autoscale_view()
        self.axes.legend()
        self.canvas.draw()
