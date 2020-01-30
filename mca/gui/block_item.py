from PySide2 import QtWidgets, QtCore, QtGui
from mca.gui.parameter_window import ParameterWindow
from mca.gui.io_items import InputItem, OutputItem


class BlockItem(QtWidgets.QGraphicsItem):

    def __init__(self, x, y, block_class):
        QtWidgets.QGraphicsItem.__init__(self)
        self.setPos(x, y)

        self.width = 100
        self.height = 100
        self.input_height = 20
        self.input_width = 10
        self.input_dist = 10
        self.output_height = 20
        self.output_width = 10
        self.output_dist = 10

        self.text = QtWidgets.QGraphicsTextItem()
        self.text.setParentItem(self)
        self.text.setPos(0, 0)
        self.text.setPlainText(block_class.name)

        self.inputs = []
        self.outputs = []
        self.block = block_class()

        self.difference = 0
        self.height = 100
        self.setToolTip("This is a test tool tip of {}".format(block_class.name))
        self.parameter_window()
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)
        for i in self.block.inputs:
            self.add_new_input(i)
        for o in self.block.outputs:
            self.add_new_output(o)
        # self.setFlags(self.ItemIsSelectable)

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(122, 122, 122)))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)

    def contextMenuEvent(self, e):
        menu = QtWidgets.QMenu(self.scene().views()[0])
        parameter_action = QtWidgets.QAction("Edit", self.scene().views()[0])
        parameter_action.triggered.connect(self.parameter_window)
        menu.addAction(parameter_action)
        inspect_action = QtWidgets.QAction("Inspect", self.scene().views()[0])
        inspect_action.triggered.connect(self.inspect_window)
        menu.addAction(inspect_action)
        menu.exec_(e.screenPos())

    @QtCore.Slot()
    def parameter_window(self):
        window = ParameterWindow(self.block)
        window.exec_()

    @QtCore.Slot()
    def inspect_window(self):
        test = InspectWindow()
        test.exec_()

    def add_new_input(self, input):
            new_input = InputItem(-self.input_width, len(self.inputs)*(self.input_height + self.input_dist) + 5,
                                  self.input_width, self.input_height, input, self)
            self.inputs.append(new_input)

    def add_new_output(self, output):
            new_output = OutputItem(self.width, len(self.outputs)*(self.output_height + self.output_dist) + 5,
                                    self.output_width, self.output_height, output, self)
            self.outputs.append(new_output)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            for i in self.inputs:
                i.update_connection_line()
            for o in self.outputs:
                o.update_connection_line()
        return super().itemChange(change, value)
