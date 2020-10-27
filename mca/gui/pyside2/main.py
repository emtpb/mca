from PySide2 import QtWidgets
import sys
import matplotlib

from mca.gui.pyside2 import mainwindow


def main():
    matplotlib.use("qt5agg")
    app = QtWidgets.QApplication(sys.argv)
    window = mainwindow.MainWindow()
    window.show()
    app.exec_()
