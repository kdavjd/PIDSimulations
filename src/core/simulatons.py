import logging

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Коэффициенты в уравнении потерь при нагревании печи, полученные из docs/oven_model
A1 = 0.004433988115689157
A2 = -2.1383429579319655
A3 = 537.4230466267185
B1 = 730.5861414838458
B2 = 595.3779940428719
K_COEFF = 0.49505773085774213
# Коэффициенты в уравнении охлаждения печи
C1 = -3.89357385551864e-06
C2 = -0.21203098043962063

OVEN_RESISTANCE = 19  # Ом - сопротивление печи
MAINS_VOLTAGE = 230  # Вольт - напряжение в сети
PIPE_MASS = 1.04  # Масса печи в Кг
AGG_TIME = 5  # Время агрегации в секундах
DT = 1  # Период симуляции в секундах


def cooling_t_loss(temperature):
    return (C1 * temperature**2 + C2) * -1


def multiply_by_pipe_mass(func):
    def wrapper(temperature):
        return func(temperature) * PIPE_MASS

    return wrapper


# согласно литературному источнику literature/sergeev1982
@multiply_by_pipe_mass
def quartz_heat_capacity(temperature):
    if temperature < 300:
        return 931.3 + 0.256 * 300 - 24 * 300 ** (-2)
    return 931.3 + 0.256 * temperature - 24 * temperature ** (-2)


def get_dt(heat_flow, power, t, a1, a2, a3, b1, b2, k_coeff):
    t_increase = heat_flow / quartz_heat_capacity(t)

    t_t_loss = (a1 * t**2 + a2 * t + a3) / quartz_heat_capacity(t)
    if t_t_loss < 0:
        t_t_loss = 0

    power_t_loss = (b1 * power + b2) / quartz_heat_capacity(t)
    if power_t_loss < 0:
        power_t_loss = 0

    if power_t_loss > k_coeff * t_t_loss:
        power_t_loss = k_coeff * t_t_loss

    dt = t_increase - cooling_t_loss(t) - t_t_loss - power_t_loss
    return t + dt


class PIDSimulations(QObject):
    simulations_data_signal = pyqtSignal(dict)

    def __init__(self, kp, ki, kd, initial_temp, final_temp, heating_rate, sim_time, thermal_inertia_coeff):
        super().__init__()
        self.logger = logging.getLogger("PIDSimulationsLogger")
        
        # Сохраняем параметры
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        self.initial_temp = float(initial_temp)
        self.final_temp = float(final_temp)
        self.heating_rate = float(heating_rate)
        self.sim_time = float(sim_time)
        self.thermal_inertia_coeff = int(thermal_inertia_coeff)

    def run_simulation(self):
        try:
            # Рассчитываем количество шагов симуляции
            dt = 0.1  # шаг времени в секундах
            num_steps = int(self.sim_time / dt)
            
            # Создаем массив целевых температур
            time_points = [i * dt for i in range(num_steps + 1)]
            target_temps = []
            
            for t in time_points:
                target_temp = min(
                    self.final_temp,
                    self.initial_temp + (self.heating_rate / 60) * t  # переводим скорость из °C/мин в °C/сек
                )
                target_temps.append(target_temp)
            
            # Запускаем симуляцию
            temperatures, errors = self._calculate_oven_temperature(
                self.initial_temp,
                target_temps,
                self.kp,
                self.ki,
                self.kd,
                dt,
                num_steps,
                self.thermal_inertia_coeff
            )
            
            return time_points, temperatures
            
        except Exception as e:
            self.logger.error(f"Error in run_simulation: {str(e)}", exc_info=True)
            raise

    def _calculate_oven_temperature(self, initial_temp, target_temperatures, kp, ki, kd, dt, num_steps, thermal_inertia_coeff):
        current_temperature = initial_temp
        oven_temperatures = [current_temperature]

        initial_target_temp = target_temperatures[0]
        initial_error = initial_target_temp - current_temperature
        errors = [initial_error]

        integral_error = initial_error * dt
        previous_error = initial_error

        # Инициализируем очередь для учета тепловой инерции
        inertia_steps = max(1, int(thermal_inertia_coeff / dt))
        contributions_queue = [0.0] * inertia_steps

        for time_step in range(num_steps):
            target_temperature = target_temperatures[time_step]
            error = target_temperature - current_temperature
            errors.append(error)

            # PID контроллер
            integral_error += error * dt
            derivative_error = (error - previous_error) / dt
            power = kp * error + ki * integral_error + kd * derivative_error
            power = max(0, min(power, 100))  # Ограничение мощности

            # Расчет тока и теплового потока
            amperage = (MAINS_VOLTAGE / OVEN_RESISTANCE) * power / 100
            heat_flow = amperage * MAINS_VOLTAGE * AGG_TIME  # Модель расчитана на период дискретизации в 5 секунд

            # Вычисление новой температуры через 5 секунд
            desired_temperature_change = get_dt(heat_flow, power, current_temperature, A1, A2, A3, B1, B2, K_COEFF)

            # Вычисление изменения температуры через 1 секунду
            delta_t = (desired_temperature_change - current_temperature) / AGG_TIME
            # Размазываем изменение во времени. Пересчет на инерциальность печи
            per_step_contribution = delta_t / inertia_steps

            # Обновление очереди тепловой инерции
            if len(contributions_queue) >= inertia_steps:
                contributions_queue.pop(0)
            contributions_queue.append(per_step_contribution)

            # Вычисление суммарного изменения температуры
            total_delta = sum(contributions_queue)

            # Обновление текущей температуры
            new_temperature = current_temperature + total_delta
            oven_temperatures.append(new_temperature)

            current_temperature = new_temperature
            previous_error = error

        return oven_temperatures, errors

    def _calculate_target_curve(self, initial_temp, final_temperature, heating_rate, sim_time):
        current_target_temp = initial_temp
        target_temperatures = [current_target_temp]
        increment = heating_rate / 60 * DT  # в градусах на секунду

        for _ in range(sim_time):
            current_target_temp = min(current_target_temp + increment, final_temperature)
            target_temperatures.append(current_target_temp)
        return target_temperatures

    @pyqtSlot(dict)
    def simulate(self, data: dict):
        self.logger.info(f"Received data for simulation: {data}")

        # Получение данных из входного словаря
        initial_temp = data.get("initial_temp", 0)
        final_temp = data.get("final_temp", 0)
        heating_rate = data.get("heating_rate", final_temp - initial_temp)
        sim_time = data.get("sim_time", 0)
        kp = data.get("kp", 0)
        ki = data.get("ki", 0)
        kd = data.get("kd", 0)
        thermal_inertia_coeff = data.get("thermal_inertia_coeff", 1)

        num_steps = int(sim_time / DT)
        time_array = [i * DT for i in range(num_steps + 1)]
        target_temperatures = self._calculate_target_curve(initial_temp, final_temp, heating_rate, num_steps)

        oven_temperatures, errors = self._calculate_oven_temperature(
            initial_temp, target_temperatures, kp, ki, kd, DT, num_steps, thermal_inertia_coeff
        )

        self.simulations_data_signal.emit({"x": time_array, "y": oven_temperatures, "label": "oven_temperature"})
        self.simulations_data_signal.emit({"x": time_array, "y": target_temperatures, "label": "target_temperature"})
        self.simulations_data_signal.emit({"x": time_array, "y": errors, "label": "error"})
