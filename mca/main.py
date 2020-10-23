import sys
from PySide2 import QtWidgets
from mca.gui.mainwindow import MainWindow
import matplotlib
matplotlib.use("qt5agg")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
