from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.language import _


class BlockList(QtWidgets.QListWidget):
    """List widget which holds all block classes."""

    def __init__(self, parent, blocks, scene, searchbar):
        """Initialize BlockList class.

        Args:
            parent: Parent of this widget.
            blocks: List of all block classes to display.
            scene: Reference of the scene where blocks get initialized.
        """
        QtWidgets.QListWidget.__init__(self, parent=parent)
        self.scene = scene

        self.search_bar = searchbar
        self.search_bar.textChanged.connect(self.show_items)
        self.setDragEnabled(True)

        self.menu = QtWidgets.QMenu()
        self.new_block_action = QtWidgets.QAction(_("Create new block"))
        self.new_block_action.triggered.connect(
            lambda: self.scene.create_block_item(self.currentItem().data(3)(),
                                                 self.width(), 10)
        )
        self.menu.addAction(self.new_block_action)
        for block in blocks:
            i = QtWidgets.QListWidgetItem()
            if block.icon_file:
                i.setIcon(QtGui.QIcon(os.path.dirname(
                    mca.__file__) + "/blocks/icons/" + block.icon_file))
            i.setData(3, block)
            i.setText(block.name)

            i.setBackgroundColor(QtGui.QColor(255, 255, 255))
            self.addItem(i)

    def mouseMoveEvent(self, event):
        """Event triggered when mouse grabbed an item from the list. Method
        allows dragging the blocks into the :class:`.BlockScene`.
        """
        mime_data = QtCore.QMimeData()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction,
                   QtCore.Qt.CopyAction)

    def mouseDoubleClickEvent(self, event):
        """Event triggered when an item in the list gets double clicked.
        The clicked block will get initialized in the :class:`.BlockScene`."""
        selected_block_class = self.currentItem().data(3)
        self.scene.create_block_item(selected_block_class(), 0, 0)

    def contextMenuEvent(self, event):
        """Event triggered when right clicking with the mouse. Opens
        the menu."""
        self.menu.exec_(event.globalPos())

    def show_items(self):
        """Show and hide certain list items depending on the
        search_bar string."""
        all_items = self.findItems("", QtCore.Qt.MatchStartsWith)
        for item in all_items:
            self.setItemHidden(item, True)
        visible_items = self.findItems(
            self.search_bar.text(), QtCore.Qt.MatchStartsWith)
        for item in visible_items:
            self.setItemHidden(item, False)


