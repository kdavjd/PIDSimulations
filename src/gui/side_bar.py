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


class PIDCoefficientsWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Создаем форму для ввода коэффициентов PID-регулятора
        layout = QFormLayout()

        # Поля ввода для Kp, Ki, Kd
        self.kp_input = QLineEdit()
        self.ki_input = QLineEdit()
        self.kd_input = QLineEdit()

        # Добавляем поля ввода на форму с соответствующими метками
        layout.addRow("Kp:", self.kp_input)
        layout.addRow("Ki:", self.ki_input)
        layout.addRow("Kd:", self.kd_input)

        # Устанавливаем форму как основной макет виджета
        self.setLayout(layout)

    def get_pid_coeffs_values(self):
        try:
            kp = float(self.kp_input.text())
            ki = float(self.ki_input.text())
            kd = float(self.kd_input.text())
            return kp, ki, kd
        except ValueError:
            return None  # Возвращаем None при ошибке преобразования


class SimulationParametersWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Создаем форму для ввода параметров симуляции
        layout = QFormLayout()

        # Поля ввода для параметров симуляции
        self.heat_flow_input = QLineEdit()
        self.initial_temp_input = QLineEdit()
        self.rate_input = QLineEdit()
        self.sim_time_input = QLineEdit()

        # Добавляем поля ввода на форму с соответствующими метками
        layout.addRow("Тепловой поток:", self.heat_flow_input)
        layout.addRow("Начальная температура:", self.initial_temp_input)
        layout.addRow("Ставка:", self.rate_input)
        layout.addRow("Время симуляции:", self.sim_time_input)

        # Устанавливаем форму как основной макет виджета
        self.setLayout(layout)

    def get_values(self):
        try:
            heat_flow = float(self.heat_flow_input.text())
            initial_temp = float(self.initial_temp_input.text())
            rate = float(self.rate_input.text())
            sim_time = float(self.sim_time_input.text())
            return heat_flow, initial_temp, rate, sim_time
        except ValueError:
            return None  # Возвращаем None при ошибке преобразования


class SimulateButtonWidget(QWidget):
    def __init__(self, callback):
        super().__init__()

        # Основной вертикальный макет для размещения кнопки симуляции
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Кнопка для запуска симуляции
        self.simulate_button = QPushButton("Провести симуляцию")

        # Подключение кнопки к переданной функции обратного вызова
        self.simulate_button.clicked.connect(callback)

        # Добавляем кнопку на макет
        layout.addWidget(self.simulate_button)

        # Добавляем растяжку для размещения кнопки внизу
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class SideBar(QWidget):
    def __init__(self, main_window):
        super().__init__()

        # Ссылка на основное окно для вызова его методов
        self.main_window = main_window

        # Основной вертикальный макет для боковой панели
        side_layout = QVBoxLayout(self)
        side_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Создаем экземпляры компонентов: виджет коэффициентов PID, параметры симуляции и кнопка
        self.pid_widget = PIDCoefficientsWidget()
        self.sim_params_widget = SimulationParametersWidget()
        self.sim_button_widget = SimulateButtonWidget(self.on_simulate)

        # Группируем виджет коэффициентов PID в область с заголовком
        pid_group = QGroupBox("Коэффициенты ПИД-регулятора")
        pid_group.setLayout(self.pid_widget.layout())
        side_layout.addWidget(pid_group)

        # Группируем виджет параметров симуляции в область с заголовком
        sim_group = QGroupBox("Параметры симуляции")
        sim_group.setLayout(self.sim_params_widget.layout())
        side_layout.addWidget(sim_group)

        # Добавляем виджет кнопки симуляции на боковую панель
        side_layout.addWidget(self.sim_button_widget)

    def on_simulate(self):
        # Получаем значения коэффициентов PID
        pid_values = self.pid_widget.get_pid_coeffs_values()
        if pid_values is None:
            return  # Завершаем метод при ошибке получения значений

        # Получаем значения параметров симуляции
        sim_params_values = self.sim_params_widget.get_values()
        if sim_params_values is None:
            return  # Завершаем метод при ошибке получения значений

        # Распаковываем все значения для передачи в симуляцию
        kp, ki, kd = pid_values
        heat_flux, initial_temp, rate, sim_time = sim_params_values

        # Запускаем симуляцию, вызывая метод run_simulation в основном окне
        self.main_window.run_simulation(kp, ki, kd, heat_flux, initial_temp, rate, sim_time)
