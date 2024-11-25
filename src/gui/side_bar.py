from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator
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

        # Добавляем подсказки о том, что означает каждый коэффициент
        self.kp_input.setPlaceholderText("Пропорциональный коэффициент")
        self.ki_input.setPlaceholderText("Интегральный коэффициент")
        self.kd_input.setPlaceholderText("Дифференциальный коэффициент")

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
            return None


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
        self.thermal_inertia_coeff_input.setText("1")

        # Устанавливаем валидаторы для целочисленных полей
        int_validator = QIntValidator()
        self.sim_time_input.setValidator(int_validator)
        self.thermal_inertia_coeff_input.setValidator(int_validator)

        # Добавляем подсказки о единицах измерения
        self.initial_temp_input.setPlaceholderText("°C")
        self.final_temp_input.setPlaceholderText("°C")
        self.heating_rate.setPlaceholderText("°C/мин")
        self.sim_time_input.setPlaceholderText("сек")
        self.thermal_inertia_coeff_input.setPlaceholderText("Безразмерный коэффициент")

        # Добавляем поля ввода на форму с соответствующими метками
        layout.addRow("Начальная температура (°C):", self.initial_temp_input)
        layout.addRow("Уставка (°C):", self.final_temp_input)
        layout.addRow("Скорость нагрева (°C/мин):", self.heating_rate)
        layout.addRow("Время симуляции (сек):", self.sim_time_input)
        layout.addRow("Коэффициент инерции (целое число):", self.thermal_inertia_coeff_input)

        # Устанавливаем форму как основной макет виджета
        self.setLayout(layout)

    def get_values(self):
        try:
            initial_temp = float(self.initial_temp_input.text())
            final_temp = float(self.final_temp_input.text())
            heating_rate = float(self.heating_rate.text())
            sim_time = int(self.sim_time_input.text())
            thermal_inertia_coeff = int(self.thermal_inertia_coeff_input.text())
            return initial_temp, final_temp, heating_rate, sim_time, thermal_inertia_coeff
        except ValueError:
            return None


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
    # Сигналы для коммуникации с другими виджетами
    simulation_data_signal = pyqtSignal(dict)
    simulation_started = pyqtSignal()  # Сигнал о начале симуляции
    simulation_stopped = pyqtSignal()  # Сигнал об окончании симуляции

    def __init__(self, min_width):
        super().__init__()
        self.setMinimumWidth(min_width)

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
        """
        Обработчик нажатия кнопки симуляции.
        Собирает данные из всех полей ввода и отправляет их через сигнал.
        """
        if not self.check_inputs_filled():
            return

        # Получаем коэффициенты PID
        pid_coeffs = self.pid_widget.get_pid_coeffs_values()
        if pid_coeffs is None:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность ввода коэффициентов PID")
            return

        # Получаем параметры симуляции
        sim_params = self.sim_params_widget.get_values()
        if sim_params is None:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность ввода параметров симуляции")
            return

        # Распаковываем значения
        kp, ki, kd = pid_coeffs
        initial_temp, final_temp, heating_rate, sim_time, thermal_inertia_coeff = sim_params

        # Создаем словарь с данными симуляции
        simulation_data = {
            "kp": kp,
            "ki": ki,
            "kd": kd,
            "initial_temp": initial_temp,
            "final_temp": final_temp,
            "heating_rate": heating_rate,
            "sim_time": sim_time,
            "thermal_inertia_coeff": thermal_inertia_coeff
        }

        # Отправляем сигнал о начале симуляции
        self.simulation_started.emit()
        # Отправляем данные
        self.simulation_data_signal.emit(simulation_data)

    def check_inputs_filled(self):
        """
        Проверяет, заполнены ли все поля ввода.
        """
        # Проверяем поля PID
        for input_field in [self.pid_widget.kp_input, self.pid_widget.ki_input, self.pid_widget.kd_input]:
            if not input_field.text():
                QMessageBox.warning(self, "Ошибка", "Заполните все коэффициенты PID")
                return False

        # Проверяем поля параметров симуляции
        sim_fields = [
            self.sim_params_widget.initial_temp_input,
            self.sim_params_widget.final_temp_input,
            self.sim_params_widget.heating_rate,
            self.sim_params_widget.sim_time_input,
            self.sim_params_widget.thermal_inertia_coeff_input
        ]
        for field in sim_fields:
            if not field.text():
                QMessageBox.warning(self, "Ошибка", "Заполните все параметры симуляции")
                return False

        return True
