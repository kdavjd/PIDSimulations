from typing import Dict, Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class PlotCanvas(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

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
        self.canvas.draw()

    def clear_plot(self):
        """Очищает все линии с графика."""
        self.axes.cla()  # Очищаем текущие оси
        self.lines.clear()  # Очищаем словарь линий
        self.canvas.draw()
