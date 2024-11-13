import sys

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSplitter, QWidget

from core.logger_config import setup_logger
from core.simulatons import PIDSimulations

from .plot_canvas import PlotCanvas
from .side_bar import SideBar

MIN_WIDTH_SIDEBAR = 80
MIN_WIDTH_PLOTCANVAS = 300
MIN_HEIGHT_MAINWINDOW = 300
SPLITTER_WIDTH = 50
COMPONENTS_MIN_WIDTH = MIN_WIDTH_SIDEBAR + MIN_WIDTH_PLOTCANVAS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симуляция ПИД-регулятора")
        self.setMinimumHeight(MIN_HEIGHT_MAINWINDOW)
        self.setMinimumWidth(COMPONENTS_MIN_WIDTH + SPLITTER_WIDTH)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        self.sidebar = SideBar(self)
        self.sidebar.setMinimumWidth(MIN_WIDTH_SIDEBAR)
        self.splitter.addWidget(self.sidebar)

        self.plot_canvas = PlotCanvas(self)
        self.plot_canvas.setMinimumWidth(MIN_WIDTH_PLOTCANVAS)
        self.splitter.addWidget(self.plot_canvas)

    def run_simulation(self, kp, ki, kd, heat_flux, initial_temp, rate, sim_time):
        t = np.linspace(0, sim_time, int(sim_time * 100))
        temp = initial_temp + heat_flux * t * np.exp(-rate * t)
        self.plot_canvas.plot(t, temp)


def main():
    setup_logger()

    app = QApplication(sys.argv)
    window = MainWindow()
    simulations = PIDSimulations()

    window.sidebar.simulation_data_signal.connect(simulations.simulate)

    window.show()
    sys.exit(app.exec())
