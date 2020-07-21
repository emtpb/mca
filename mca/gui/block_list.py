from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.language import _


class BlockList(QtWidgets.QListWidget):
    """List widget which holds all block classes."""
    resized = QtCore.Signal()

    def __init__(self, parent, blocks, scene):
        """Initialize BlockList class.

        Args:
            parent: Parent of this widget.
            blocks: List of all block classes to display.
            scene: Reference of the scene where blocks get initialized.
        """
        QtWidgets.QListWidget.__init__(self, parent=parent)
        self.scene = scene
        self.setDragEnabled(True)
        self.setGeometry(0, 0, self.parent().width() * 0.2,
                         self.parent().height() * 0.7)

        self.menu = QtWidgets.QMenu()
        self.new_block_action = QtWidgets.QAction(_("Create new block"))
        self.new_block_action.triggered.connect(
            lambda: self.scene.create_block_item(self.width(), 10,
                                                 self.currentItem().data(3)())
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
        self.setMaximumSize(QtCore.QSize(200, 16777215))

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

