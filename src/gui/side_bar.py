from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class SideBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        side_layout = QVBoxLayout(self)
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
        self.heat_flow_input = QLineEdit()
        self.initial_temp_input = QLineEdit()
        self.rate_input = QLineEdit()
        self.sim_time_input = QLineEdit()
        sim_layout.addRow("Тепловой поток:", self.heat_flow_input)
        sim_layout.addRow("Начальная температура:", self.initial_temp_input)
        sim_layout.addRow("Ставка:", self.rate_input)
        sim_layout.addRow("Время симуляции:", self.sim_time_input)
        sim_group.setLayout(sim_layout)
        side_layout.addWidget(sim_group)

        # Прокладка для размещения кнопки внизу
        side_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))  # noqa: E501

        # Кнопка "Провести симуляцию"
        self.simulate_button = QPushButton("Провести симуляцию")
        self.simulate_button.clicked.connect(self.on_simulate)
        side_layout.addWidget(self.simulate_button)

    def on_simulate(self):
        # Получение значений из полей ввода
        try:
            kp = float(self.kp_input.text())
            ki = float(self.ki_input.text())
            kd = float(self.kd_input.text())
            heat_flux = float(self.heat_flow_input.text())
            initial_temp = float(self.initial_temp_input.text())
            rate = float(self.rate_input.text())
            sim_time = float(self.sim_time_input.text())
        except ValueError:
            return

        # Запуск симуляции через основное окно
        self.main_window.run_simulation(kp, ki, kd, heat_flux, initial_temp, rate, sim_time)
