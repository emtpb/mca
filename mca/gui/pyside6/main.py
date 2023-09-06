import os
import platform
import sys

import PySide6
import matplotlib
from PySide6 import QtWidgets, QtCore

# Make sure the plugin path is set correctly
pyside_path = os.path.dirname(PySide6.__file__)
if platform.system() == "Linux":
    plugin_path = os.path.join(pyside_path, "Qt", "plugins")
    os.environ["QT_PLUGIN_PATH"] = plugin_path
elif platform.system() == "Windows":
    plugin_path = os.path.join(pyside_path, "plugins")
    os.environ["QT_PLUGIN_PATH"] = plugin_path


def main(file=None):
    """Main function for the PySide GUI of mca. Switches the matplotlib
    backend to Qt5 and opens the :class:`.MainWindow` .

    Args:
        file (str): File to open on startup.
    """
    from mca.gui.pyside6 import main_window
    matplotlib.use("qt5agg")
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = PySide6.QtWidgets.QApplication(sys.argv)
    window = main_window.MainWindow(file=file)
    window.show()
    app.exec_()
