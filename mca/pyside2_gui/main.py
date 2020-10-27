from PySide2 import QtWidgets
import sys
import matplotlib

from mca.pyside2_gui.mainwindow import MainWindow


def main():
    matplotlib.use("qt5agg")
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
