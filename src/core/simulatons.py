import logging

from PyQt6.QtCore import QObject, pyqtSlot


class PIDSimulations(QObject):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("PIDSimulationsLogger")

    @pyqtSlot(dict)
    def simulate(self, data):
        self.logger.info(f"Received data for simulation: {data}")
        pass
