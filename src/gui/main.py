import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSplitter, QWidget

from src.core.logger_config import setup_logger
from src.core.simulatons import PIDSimulations
from src.gui.plot_canvas import PlotCanvas
from src.gui.side_bar import SideBar

# Добавляем путь к корневой директории проекта
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)


MIN_WIDTH_SIDEBAR = 80
MIN_WIDTH_PLOTCANVAS = 300
MIN_HEIGHT_MAINWINDOW = 300
SPLITTER_WIDTH = 50
COMPONENTS_MIN_WIDTH = MIN_WIDTH_SIDEBAR + MIN_WIDTH_PLOTCANVAS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симуляция ПИД-регулятора")
        self.setMinimumWidth(COMPONENTS_MIN_WIDTH)
        self.setMinimumHeight(MIN_HEIGHT_MAINWINDOW)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create and setup the splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(SPLITTER_WIDTH)

        # Create sidebar and plot canvas
        self.side_bar = SideBar(MIN_WIDTH_SIDEBAR)
        self.plot_canvas = PlotCanvas()  # Убираем передачу ширины
        self.plot_canvas.setMinimumWidth(MIN_WIDTH_PLOTCANVAS)  # Устанавливаем минимальную ширину через метод

        # Add widgets to splitter
        splitter.addWidget(self.side_bar)
        splitter.addWidget(self.plot_canvas)

        # Add splitter to layout
        layout.addWidget(splitter)


def main():
    app = QApplication(sys.argv)
    setup_logger()
    window = MainWindow()
    simulations = PIDSimulations()

    window.side_bar.simulation_coeffs_signal.connect(simulations.request_slot)
    simulations.simulations_data_signal.connect(window.plot_canvas.plot_data)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
