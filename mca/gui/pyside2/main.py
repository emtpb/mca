import os
import platform
import sys

import PySide2
import matplotlib
from PySide2 import QtWidgets, QtCore

# Make sure the plugin path is set correctly
pyside_path = os.path.dirname(PySide2.__file__)
if platform.system() == "Linux":
    plugin_path = os.path.join(pyside_path, "Qt", "plugins")
    os.environ["QT_PLUGIN_PATH"] = plugin_path
elif platform.system() == "Windows":
    plugin_path = os.path.join(pyside_path, "plugins")
    os.environ["QT_PLUGIN_PATH"] = plugin_path


def main():
    """Main function for the PySide2 GUI of mca. Switches the matplotlib
    backend to Qt5 and opens the :class:`.MainWindow` ."""
    from mca.gui.pyside2 import main_window
    matplotlib.use("qt5agg")
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = PySide2.QtWidgets.QApplication(sys.argv)
    window = main_window.MainWindow()
    window.show()
    app.exec_()
