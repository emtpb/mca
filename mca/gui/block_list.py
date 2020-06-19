from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca


class BlockList(QtWidgets.QListWidget):
    """List widget which holds all block classes."""
    resized = QtCore.Signal()

    def __init__(self, parent, blocks):
        """Initialize BlockList class.

        Args:
            parent: Parent of this widget.
            blocks: List of all block classes to display.
        """
        QtWidgets.QListWidget.__init__(self, parent=parent)
        self.setDragEnabled(True)
        self.setGeometry(0, 0, self.parent().width() * 0.2,
                         self.parent().height() * 0.7)
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
        allows dragging the block classes into the :class:`.BlockScene`.
        """
        mimeData = QtCore.QMimeData()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction,
                   QtCore.Qt.CopyAction)
