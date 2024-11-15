import sys

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


def main():
    setup_logger()

    app = QApplication(sys.argv)
    window = MainWindow()
    simulations = PIDSimulations()

    window.sidebar.simulation_data_signal.connect(simulations.simulate)
    simulations.simulations_data_signal.connect(window.plot_canvas.request_slot)

    window.show()
    sys.exit(app.exec())
