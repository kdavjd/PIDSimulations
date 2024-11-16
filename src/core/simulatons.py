import logging

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Коэффициенты в уравнении потерь при нагревании печи, полученные из docs/oven_model
A1 = -0.004511200300912059
A2 = 2.97936894852502
A3 = -1070.2463559702983
B1 = 62.45356998903521
B2 = 2.2915522070523324
# Коэффициенты в уравнении охлаждения печи
C1 = -3.89357385551864e-06
C2 = -0.21203098043962063

OVEN_RESISTANCE = 19  # Ом - сопротивление печи
MAINS_VOLTAGE = 230  # Вольт - напряжение в сети
PIPE_MASS = 1.04  # Масса печи в Кг
AGG_TIME = 5  # Время агрегации в секундах


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


def get_dt(heat_flow, power, t, a1, a2, a3, b1, b2):
    t_increase = heat_flow / quartz_heat_capacity(t)
    t_t_loss = (a1 * t**2 + a2 * t + a3) / quartz_heat_capacity(t)
    power_t_loss = (b1 * power + b2) / quartz_heat_capacity(t)
    dt = t_increase - cooling_t_loss(t) - t_t_loss - power_t_loss
    return t + (dt / AGG_TIME)


class PIDSimulations(QObject):
    simulations_data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("PIDSimulationsLogger")

    def _calculate_oven_curve(self, initial_temp, power, sim_time):
        current_temperature = initial_temp
        oven_temperatures = [current_temperature]

        amperage = (MAINS_VOLTAGE / OVEN_RESISTANCE) * power / 100
        heat_flow = amperage * MAINS_VOLTAGE * AGG_TIME  # тепловой поток на 5 секунд

        for _ in range(sim_time):
            # новая температура через 1 секнду
            new_temperature = get_dt(heat_flow, power, current_temperature, A1, A2, A3, B1, B2)
            oven_temperatures.append(new_temperature)
            current_temperature = new_temperature
        return oven_temperatures

    def _calculate_target_curve(self, initial_temp, final_temperature, heating_rate, sim_time):
        current_target_temp = initial_temp
        target_temperatures = [current_target_temp]
        increment = heating_rate / 60  # в градусах на секунду

        for _ in range(sim_time):
            current_target_temp = min(current_target_temp + increment, final_temperature)
            target_temperatures.append(current_target_temp)
        return target_temperatures

    @pyqtSlot(dict)
    def simulate(self, data: dict):
        self.logger.info(f"Received data for simulation: {data}")

        initial_temp = data.get("initial_temp", 0)
        final_temperature = data.get("final_temp", 0)
        heating_rate = data.get("heating_rate", final_temperature - initial_temp)
        sim_time = data.get("sim_time", 0)

        # задаемся мощностью для отладки
        power = 20

        time_array = list(range(sim_time + 1))  # в секндах
        target_temperatures = self._calculate_target_curve(initial_temp, final_temperature, heating_rate, sim_time)
        oven_temperatures = self._calculate_oven_curve(initial_temp, power, sim_time)

        # Посылаем сигнал для температуры печи
        self.simulations_data_signal.emit({"x": time_array, "y": oven_temperatures, "label": "oven_temperatures"})

        # Посылаем сигнал для целевой температуры
        self.simulations_data_signal.emit({"x": time_array, "y": target_temperatures, "label": "target_temperatures"})
