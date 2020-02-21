from PySide2 import QtWidgets, QtCore
import inspect

import mca.blocks
from mca.gui import block_list, block_display


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.resize(1000, 800)
        self.setWindowTitle("MCA")

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Close Application")
        exit_action.triggered.connect(self.exit_app)
        self.file_menu.addAction(exit_action)

        self.main_widget = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.blocks = [m[1] for m in inspect.getmembers(mca.blocks, inspect.isclass)]
        self.main_widget.addWidget(block_list.BlockList(self.main_widget, self.blocks))

        self.scene = block_display.BlockScene(self.main_widget)
        self.view = block_display.BlockView(scene=self.scene, parent=self.main_widget)
        self.view.show()
        self.main_widget.addWidget(self.view)

        self.main_widget.setSizes([50, 200])
        self.setCentralWidget(self.main_widget)

    @QtCore.Slot()
    def exit_app(self):
        QtWidgets.QApplication.quit()
