# logger_config.py
import logging


def setup_logger():
    # Настраиваем глобальный логгер с именем 'PIDSimulationsLogger'
    logger = logging.getLogger("PIDSimulationsLogger")
    logger.setLevel(logging.INFO)

    # Создаем обработчик для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Устанавливаем формат для консольного вывода
    console_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(message)s", datefmt="%H.%M.%S")
    console_handler.setFormatter(console_formatter)

    # Добавляем обработчики к логгеру, если они ещё не добавлены
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
    else:
        pass
    return logger
