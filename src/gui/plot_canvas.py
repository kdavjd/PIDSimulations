import logging
from typing import Dict, Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QWidget

CANVAS_BIG_SIZE = 12
CANVAS_MEDIUM_SIZE = 10
CANVAS_SMALL_SIZE = 8


class PlotCanvas(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger("PIDSimulationsLogger")

        # Настройка стиля matplotlib
        plt.style.use(["science", "no-latex", "notebook", "grid"])
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
        self.lines: Dict[str, Line2D] = {}

        # Настройка компоновки для PlotCanvas
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Добавляем панель инструментов сверху
        layout.addWidget(self.canvas)  # Добавляем холст под панелью инструментов
        self.setLayout(layout)

    @pyqtSlot(dict)
    def request_slot(self, data: dict):
        self.logger.debug(f"Received data: {data}")
        x = data.get("x")
        y = data.get("y")
        label = data.get("label")
        self.plot(x, y, label)

    def plot(self, x, y, label="default"):
        """Отображает линию на графике с указанной меткой."""
        if label in self.lines:
            # Обновляем данные существующей линии, если она уже есть
            self.lines[label].set_data(x, y)
        else:
            # Создаем новую линию и добавляем ее в словарь
            (line,) = self.axes.plot(x, y, label=label)
            self.lines[label] = line
        self.axes.relim()
        self.axes.autoscale_view()
        self.axes.legend()  # Добавляем легенду
        self.canvas.draw()

    def clear_plot(self):
        """Очищает все линии с графика."""
        self.axes.cla()  # Очищаем текущие оси
        self.lines.clear()  # Очищаем словарь линий
        self.canvas.draw()
