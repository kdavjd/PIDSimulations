from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
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

        # Устанавливаем значения по умолчанию
        self.kp_input.setText("1")
        self.ki_input.setText("1")
        self.kd_input.setText("1")

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
        self.heating_rate = QLineEdit()
        self.initial_temp_input = QLineEdit()
        self.final_temp_input = QLineEdit()
        self.sim_time_input = QLineEdit()
        self.thermal_inertia_coeff_input = QLineEdit()

        # Устанавливаем значения по умолчанию
        self.initial_temp_input.setText("25")
        self.final_temp_input.setText("250")
        self.heating_rate.setText("10")
        self.sim_time_input.setText("500")
        self.thermal_inertia_coeff_input.setText("0.5")

        # Добавляем поля ввода на форму с соответствующими метками
        layout.addRow("Начальная температура:", self.initial_temp_input)
        layout.addRow("Уставка:", self.final_temp_input)
        layout.addRow("Скорость нагрева:", self.heating_rate)
        layout.addRow("Время симуляции:", self.sim_time_input)
        layout.addRow("Коэффициент инерции:", self.thermal_inertia_coeff_input)

        # Устанавливаем форму как основной макет виджета
        self.setLayout(layout)

    def get_values(self):
        try:
            power = float(self.heating_rate.text())
            initial_temp = float(self.initial_temp_input.text())
            final_temp = float(self.final_temp_input.text())
            sim_time = int(self.sim_time_input.text())
            thermal_inertia_coeff = float(self.thermal_inertia_coeff_input.text())
            return power, initial_temp, final_temp, sim_time, thermal_inertia_coeff
        except ValueError:
            return None  # Возвращаем None при ошибке преобразования


class SimulateButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Основной вертикальный макет для размещения кнопки симуляции
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Кнопка для запуска симуляции
        self.simulate_button = QPushButton("Провести симуляцию")

        # Добавляем кнопку на макет
        layout.addWidget(self.simulate_button)

        # Добавляем растяжку для размещения кнопки внизу
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class SideBar(QWidget):
    # Определяем сигнал, который будет излучать собранные данные
    simulation_data_signal = pyqtSignal(dict)

    def __init__(self, main_window):
        super().__init__()

        # Ссылка на основное окно для вызова его методов
        self.main_window = main_window

        # Основной вертикальный макет для боковой панели
        side_layout = QVBoxLayout(self)
        side_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Создаем экземпляры компонентов: виджет коэффициентов PID, параметры симуляции и кнопку
        self.pid_widget = PIDCoefficientsWidget()
        self.sim_params_widget = SimulationParametersWidget()
        self.sim_button_widget = SimulateButtonWidget()

        # Подключаем нажатие кнопки к методу для обработки данных и излучения сигнала
        self.sim_button_widget.simulate_button.clicked.connect(self.on_simulate)

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
        # Проверяем заполненность всех полей
        if not self.check_inputs_filled():
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        # Получаем значения коэффициентов PID
        pid_values = self.pid_widget.get_pid_coeffs_values()
        if pid_values is None:
            QMessageBox.warning(self, "Ошибка", "Некорректные значения коэффициентов PID.")
            return

        # Получаем значения параметров симуляции
        sim_params_values = self.sim_params_widget.get_values()
        if sim_params_values is None:
            QMessageBox.warning(self, "Ошибка", "Некорректные значения параметров симуляции.")
            return

        # Формируем словарь с собранными данными
        data = {
            "kp": pid_values[0],
            "ki": pid_values[1],
            "kd": pid_values[2],
            "heating_rate": sim_params_values[0],
            "initial_temp": sim_params_values[1],
            "final_temp": sim_params_values[2],
            "sim_time": sim_params_values[3],
            "thermal_inertia_coeff": sim_params_values[4],
        }

        # Излучаем сигнал с данными
        self.simulation_data_signal.emit(data)

    def check_inputs_filled(self):
        """Проверяет, заполнены ли все поля ввода."""
        inputs = [
            self.pid_widget.kp_input,
            self.pid_widget.ki_input,
            self.pid_widget.kd_input,
            self.sim_params_widget.heating_rate,
            self.sim_params_widget.initial_temp_input,
            self.sim_params_widget.final_temp_input,
            self.sim_params_widget.sim_time_input,
            self.sim_params_widget.thermal_inertia_coeff_input,
        ]
        return all(input_field.text().strip() for input_field in inputs)
