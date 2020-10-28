from PySide2 import QtWidgets
import sys
import matplotlib

from mca.gui.pyside2 import main_window


def main():
    """Main function for the PySide2 GUI of mca. Switches the matplotlib
    backend to Qt5 and opens the :class:`.MainWindow` ."""
    matplotlib.use("qt5agg")
    app = QtWidgets.QApplication(sys.argv)
    window = main_window.MainWindow()
    window.show()
    app.exec_()
