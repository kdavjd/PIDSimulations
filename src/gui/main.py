import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QPushButton, QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PIDSimulationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симуляция ПИД-регулятора")
        self.initUI()

    def initUI(self):
        # Главный виджет и макет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Боковая панель
        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Область для коэффициентов ПИД-регулятора
        pid_group = QGroupBox("Коэффициенты ПИД-регулятора")
        pid_layout = QFormLayout()
        self.kp_input = QLineEdit()
        self.ki_input = QLineEdit()
        self.kd_input = QLineEdit()
        pid_layout.addRow("Kp:", self.kp_input)
        pid_layout.addRow("Ki:", self.ki_input)
        pid_layout.addRow("Kd:", self.kd_input)
        pid_group.setLayout(pid_layout)
        side_layout.addWidget(pid_group)

        # Область для параметров симуляции
        sim_group = QGroupBox("Параметры симуляции")
        sim_layout = QFormLayout()
        self.heat_flux_input = QLineEdit()
        self.initial_temp_input = QLineEdit()
        self.rate_input = QLineEdit()
        self.sim_time_input = QLineEdit()
        sim_layout.addRow("Тепловой поток:", self.heat_flux_input)
        sim_layout.addRow("Начальная температура:", self.initial_temp_input)
        sim_layout.addRow("Ставка:", self.rate_input)
        sim_layout.addRow("Время симуляции:", self.sim_time_input)
        sim_group.setLayout(sim_layout)
        side_layout.addWidget(sim_group)

        # Прокладка для размещения кнопки внизу
        side_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Кнопка "Провести симуляцию"
        self.simulate_button = QPushButton("Провести симуляцию")
        self.simulate_button.clicked.connect(self.run_simulation)
        side_layout.addWidget(self.simulate_button)

        # Добавление боковой панели в главный макет
        main_layout.addWidget(side_panel)

        # Оси matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

    def run_simulation(self):
        # Получение значений из полей ввода
        try:
            kp = float(self.kp_input.text())
            ki = float(self.ki_input.text())
            kd = float(self.kd_input.text())
            heat_flux = float(self.heat_flux_input.text())
            initial_temp = float(self.initial_temp_input.text())
            rate = float(self.rate_input.text())
            sim_time = float(self.sim_time_input.text())
        except ValueError:
            print("Пожалуйста, введите корректные числовые значения.")
            return

        # Пример симуляции (замените на вашу логику)
        t = np.linspace(0, sim_time, int(sim_time * 100))
        temp = initial_temp + heat_flux * t * np.exp(-rate * t)

        # Очистка и обновление графика
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(t, temp)
        ax.set_xlabel('Время')
        ax.set_ylabel('Температура')
        ax.set_title('Результаты симуляции')
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = PIDSimulationApp()
    window.show()
    sys.exit(app.exec())