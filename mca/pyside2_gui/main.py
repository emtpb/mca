import sys
from PySide2 import QtWidgets
from mca.pyside2_gui.mainwindow import MainWindow
import matplotlib


def main():
    matplotlib.use("qt5agg")
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
