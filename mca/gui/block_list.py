from PySide2 import QtWidgets, QtCore, QtGui


class BlockList(QtWidgets.QListWidget):
    resized = QtCore.Signal()

    def __init__(self, parent, blocks):
        QtWidgets.QListWidget.__init__(self, parent=parent)
        self.setDragEnabled(True)
        self.setGeometry(0, 0, self.parent().width() * 0.2, self.parent().height() * 0.7)
        for block in blocks:
            i = QtWidgets.QListWidgetItem()
            i.setData(1, block)
            i.setText(i.data(1).name)
            i.setBackgroundColor(QtGui.QColor(255, 255, 255))
            self.addItem(i)
        self.setMaximumSize(QtCore.QSize(200, 16777215))

    def mouseMoveEvent(self, event):
        mimeData = QtCore.QMimeData()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction,
                   QtCore.Qt.CopyAction)