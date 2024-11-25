import logging
from typing import Dict, Optional
from PyQt6.QtWidgets import QMessageBox

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
        plt.style.use(['seaborn-v0_8-darkgrid'])  # Используем встроенный стиль вместо science
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

        # Флаг состояния симуляции
        self.simulation_running = False

    @pyqtSlot()
    def start_simulation(self):
        """Начало новой симуляции"""
        self.simulation_running = True
        # Очищаем график для новой симуляции
        self.axes.clear()
        self.lines.clear()
        self.canvas.draw()

    @pyqtSlot()
    def stop_simulation(self):
        """Остановка симуляции"""
        self.simulation_running = False

    @pyqtSlot(dict)
    def request_slot(self, data: dict):
        try:
            if not self.simulation_running:
                self.logger.warning("Received data while simulation is not running")
                return
            
            self.logger.debug(f"Received data: {data}")
            
            # Проверяем наличие необходимых данных
            required_keys = ["kp", "ki", "kd", "initial_temp", "final_temp", "heating_rate", "sim_time", "thermal_inertia_coeff"]
            for key in required_keys:
                if key not in data:
                    self.logger.error(f"Missing required key in data: {key}")
                    return
            
            # Создаем симуляцию
            from core.simulatons import PIDSimulations
            simulation = PIDSimulations(
                kp=data["kp"],
                ki=data["ki"],
                kd=data["kd"],
                initial_temp=data["initial_temp"],
                final_temp=data["final_temp"],
                heating_rate=data["heating_rate"],
                sim_time=data["sim_time"],
                thermal_inertia_coeff=data["thermal_inertia_coeff"]
            )
            
            # Получаем данные симуляции и время
            sim_time = float(data["sim_time"])
            dt = 0.1  # шаг времени в секундах
            num_steps = int(sim_time / dt)
            time_points = [i * dt for i in range(num_steps + 1)]
            
            # Очищаем график перед новой симуляцией
            self.axes.clear()
            self.lines.clear()
            
            # Получаем температуры и целевые значения
            temperatures, target_temps = simulation.run_simulation()
            
            # Вычисляем ошибку
            errors = [target - actual for target, actual in zip(target_temps, temperatures)]
            
            # Отображаем все три кривые
            self.plot(time_points, temperatures, "Температура")
            self.plot(time_points, target_temps, "Уставка")
            self.plot(time_points, errors, "Ошибка")
            
        except Exception as e:
            self.logger.error(f"Error in request_slot: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при симуляции: {str(e)}")

    def plot(self, x, y, label="default"):
        try:
            if not self.simulation_running:
                self.logger.warning("Attempt to plot while simulation is not running")
                return

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
            
        except Exception as e:
            self.logger.error(f"Error in plot method: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при отрисовке графика: {str(e)}")
