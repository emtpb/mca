from PySide2 import QtWidgets, QtGui, QtCore
import os
import qdarkstyle

from mca import config
from mca.framework import save, load
from mca.gui.pyside2 import block_explorer, block_display, about_window
from mca.language import _


class MainWindow(QtWidgets.QMainWindow):
    """Main window of the mca. Holds the main widgets of the application.

    Attributes:
        conf: Reference of the user config :class:`.Config`.
        main_widget: Main splitter widget with horizontal layout
                     for child widgets.
        block_scene: :class:`.BlockScene` to manage and hold blocks.
        block_view: :class:`.BlockView` to visualize the items of the
              :class:`.BlockScene`.
        block_explorer: Widget for the block explorer plane.
        save_file_path: Path of the file to save the block structure to.
    """

    def __init__(self):
        """Initializes MainWindow."""
        QtWidgets.QMainWindow.__init__(self)
        self.resize(1000, 800)

        self.conf = config.Config()

        self.about_window = about_window.AboutWindow(self)

        self.setWindowIcon(QtGui.QIcon(
            os.path.dirname(__file__) + "/../../images/emt_logo.png"))
        if self.conf["theme"] == "default":
            self.set_default_theme()
        else:
            self.set_dark_theme()

        self.open_recent_menu = None
        self.save_file_path = None

        self.init_menu()

        self.modified = False

        self.main_widget = QtWidgets.QSplitter(self)

        self.block_scene = block_display.BlockScene(self.main_widget)
        self.block_view = block_display.BlockView(scene=self.block_scene, parent=self)
        self.block_view.show()

        view_widget = QtWidgets.QWidget()
        view_widget.setLayout(QtWidgets.QVBoxLayout())
        self.view_tool_bar = QtWidgets.QToolBar()
        self.init_view_toolbar()
        view_widget.layout().addWidget(self.view_tool_bar)
        view_widget.layout().addWidget(self.block_view)

        self.block_explorer = block_explorer.BlockExplorer(self.block_scene)
        self.block_scene.block_list = self.block_explorer.block_list

        self.main_widget.addWidget(self.block_explorer)
        self.main_widget.addWidget(view_widget)
        self.setCentralWidget(self.main_widget)
        # Save warning message
        self.save_warning_message = QtWidgets.QMessageBox(
            parent=self,
            icon=QtWidgets.QMessageBox.Warning,
            text=_("The document has been modified.\nDo you want to save your changes?"),
        )
        self.save_warning_message.setWindowTitle(_("MCA"))
        self.save_warning_message.setStandardButtons(QtWidgets.QMessageBox.Yes
                                                     | QtWidgets.QMessageBox.Cancel
                                                     | QtWidgets.QMessageBox.No)
        self.save_warning_message.button(QtWidgets.QMessageBox.Yes).setText(_("Yes"))
        self.save_warning_message.button(QtWidgets.QMessageBox.Cancel).setText(
            _("Cancel"))
        self.save_warning_message.button(QtWidgets.QMessageBox.No).setText(
            _("No"))

    def init_menu(self):

        menu = self.menuBar()
        file_menu = menu.addMenu(_("File"))
        language_menu = menu.addMenu(_("Language"))
        view_menu = menu.addMenu(_("View"))

        open_about_window = QtWidgets.QAction(_("About"), self)
        open_about_window.triggered.connect(self.about_window.show)

        menu.addAction(open_about_window)
        languages = [("Deutsch", "de"), ("English", "en")]

        for i in languages:
            action = QtWidgets.QAction(i[0], self)
            action.triggered.connect(self.change_language(i[1]))
            language_menu.addAction(action)

        new_action = QtWidgets.QAction(_("New"), self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QtWidgets.QAction(_("Open"), self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        self.open_recent_menu = QtWidgets.QMenu(_("Open Recent"), self)
        self.update_recent_menu()

        file_menu.addMenu(self.open_recent_menu)

        save_action = QtWidgets.QAction(_("Save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        file_menu.addAction(save_action)

        save_as_action = QtWidgets.QAction(_("Save as"), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        clear_action = QtWidgets.QAction(_("Clear all blocks"), self)
        clear_action.triggered.connect(self.clear_all_blocks)
        file_menu.addAction(clear_action)

        exit_action = QtWidgets.QAction(_("Exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip(_("Close Application"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        theme_menu = view_menu.addMenu(_("Theme"))
        default_theme_action = QtWidgets.QAction(_("Default"), self)
        default_theme_action.triggered.connect(self.set_default_theme)
        dark_theme_action = QtWidgets.QAction(_("Dark"), self)
        dark_theme_action.triggered.connect(self.set_dark_theme)
        theme_menu.addAction(default_theme_action)
        theme_menu.addAction(dark_theme_action)

    def init_view_toolbar(self):
        """Initializes the toolbar for the block view."""
        self.view_tool_bar = QtWidgets.QToolBar()
        self.view_tool_bar.addAction(self.block_view.zoom_in_action)
        self.view_tool_bar.addAction(self.block_view.zoom_out_action)
        self.view_tool_bar.addAction(self.block_view.zoom_original_action)

    def closeEvent(self, event):
        """Method invoked when the application gets closed. Asks the user to
        save unsaved changes.
        """
        if self.save_maybe():
            event.accept()
        else:
            event.ignore()

    def new_file(self):
        """Creates a new file."""
        if self.save_maybe():
            self.block_scene.clear()
            self.save_file_path = None
            self.modified = False

    def open_file_dialog(self):
        """Opens file dialog to let the user select a file to open."""
        if self.save_maybe():
            file_name = QtWidgets.QFileDialog.getOpenFileName(
                self, _("Select a file to open"), self.conf["load_file_dir"],
                "json (*json)")
            if file_name[0]:
                self.open_file(file_name[0])

    def open_file_direct(self, file_name):
        """Returns a function that opens a specific file.

        Args:
            file_name (str): Path of the file to open.
        """
        def tmp():
            if self.save_maybe():
                self.open_file(file_name)
        return tmp

    def open_file(self, file_path):
        """Opens given file path. Loads the blocks in the file into the block
        structure and then tells the :class:`.BlockScene` to visualize them.

        Args:
            file_path (str): Path of the file to open.
        """
        self.block_scene.clear()
        loaded_blocks = load.load_block_structure(file_path)
        self.save_file_path = file_path
        self.conf["load_file_dir"] = file_path
        if file_path in self.conf["recent_files"]:
            self.conf["recent_files"].remove(file_path)
        self.conf["recent_files"] = [file_path] + self.conf["recent_files"][:3]
        self.update_recent_menu()
        self.block_scene.create_blocks(loaded_blocks)
        self.modified = False

    def update_recent_menu(self):
        """Updates the actions in the recent menu based on the last chosen
        files.
        """
        self.open_recent_menu.clear()
        for file_name in self.conf["recent_files"]:
            open_file_action = QtWidgets.QAction(file_name, self)
            open_file_action.triggered.connect(
                self.open_file_direct(file_name))
            self.open_recent_menu.addAction(open_file_action)

    def save_file_as(self):
        """Opens file dialog and save the current state to the given file.

        Returns:
            bool: True, if saving has been successful. False, otherwise.
        """
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, _("Save"), self.conf["save_file_dir"], "json (*.json)")[0]
        if not file_name:
            return False
        elif "." in file_name and not file_name.endswith(".json"):
            QtWidgets.QMessageBox.warning(
                self, _("MCA"),
                _("File has to be a .json"), QtWidgets.QMessageBox.Ok)
            return False
        if not file_name.endswith(".json"):
            file_name += ".json"
        self.save_file_path = file_name
        self.conf["save_file_dir"] = os.path.dirname(self.save_file_path)
        self.save_file()

        self.conf["recent_files"] = [file_name] + self.conf["recent_files"][:3]
        self.update_recent_menu()
        return True

    def save_file(self):
        """Saves the current state.

        Opens up a file dialog if no safe file path has been specified yet.

        Returns:
            bool: True, if the file has been saved successfully.
                  Otherwise False.
        """
        if self.save_file_path:
            save.save_block_structure(self.save_file_path)
            self.modified = False
            return True
        else:
            return self.save_file_as()

    def save_maybe(self):
        """Opens up a message dialogue asking if the user wants to save
        changes if the document has been modified.

        Returns:
            bool: True, if the action was accepted regardless
                  if the file was saved or not. False, if the action was
                  cancelled.
        """
        if self.modified:
            result = self.save_warning_message.exec_()
        else:
            return True
        if result == QtWidgets.QMessageBox.Yes:
            return self.save_file()
        elif result == QtWidgets.QMessageBox.No:
            return True
        else:
            return False

    def clear_all_blocks(self):
        """Clears the :class:`.BlockScene` from all blocks."""
        message_box = QtWidgets.QMessageBox(parent=self,
                                            icon=QtWidgets.QMessageBox.Question,
                                            text=_("Are you sure you want to remove all blocks?"))
        message_box.setWindowTitle(_("MCA"))
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        message_box.button(QtWidgets.QMessageBox.Cancel).setText(_("Cancel"))
        message_box.button(QtWidgets.QMessageBox.Yes).setText(
            _("Yes"))
        result = message_box.exec_()
        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            self.block_scene.clear()

    @property
    def modified(self):
        """Gets or sets whether there are any unsaved changes.

        Setting this property causes an update of the window title.
        """
        return self._modified

    @modified.setter
    def modified(self, value):
        self._modified = value
        if self.save_file_path:
            show_file = self.save_file_path
        else:
            show_file = _("untitled.json")
        if self._modified:
            show_file = "*" + show_file
        self.setWindowTitle("{} - {}".format(show_file, _("MCA")))

    def set_default_theme(self):
        """Sets the application style to default."""
        self.conf["theme"] = "default"
        app = QtWidgets.QApplication.instance()
        app.setStyleSheet("")

    def set_dark_theme(self):
        """Sets the application style to dark."""
        self.conf["theme"] = "dark"
        app = QtWidgets.QApplication.instance()
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        self.style().setObjectName("qdarkstyle")

    def change_language(self, language):
        """Returns a function which changes the language in the config.

        Args:
            language (str): Language the function changes to.
        """

        def tmp():
            self.conf["language"] = language
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText(_("Changes will be applied after restart."))
            msg_box.exec()
        return tmp
