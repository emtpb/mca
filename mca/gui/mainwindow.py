from PySide2 import QtWidgets, QtCore
import inspect
import importlib

import mca.blocks
from mca.gui import block_list, block_display
from mca import config
from mca.language import _


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.exit_code_reboot = 105
        self.resize(1000, 800)
        self.setWindowTitle("MCA")

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.language_menu = self.menu.addMenu("Language")
        languages = [("Deutsch", "de"), ("English", "en")]
        for i in languages:
            action = QtWidgets.QAction(i[0], self)
            action.triggered.connect(self.change_language(i[1]))
            self.language_menu.addAction(action)
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

    def change_language(self, new_language):
        def tmp():
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText("Changes will be applied after restart.")
            msg_box.exec()
            config.Config()["language"] = new_language
        return tmp
