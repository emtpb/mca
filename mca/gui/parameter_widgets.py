from PySide2 import QtWidgets


class FloatWidget(QtWidgets.QLineEdit):
    def __init__(self, parameter, parent):
        QtWidgets.QLineEdit.__init__(self)
        self.parameter = parameter
        self.setParent(parent)

    def set_parameter(self):
        self.parameter.value = float(self.text())


class IntWidget(QtWidgets.QLineEdit):
    def __init__(self, parameter, parent):
        QtWidgets.QLineEdit.__init__(self)
        self.parameter = parameter
        self.setParent(parent)

    def set_parameter(self):
        self.parameter.value = int(self.text())


class ChoiceWidget(QtWidgets.QComboBox):
    def __init__(self, parameter, parent):
        QtWidgets.QComboBox.__init__(self)
        self.parameter = parameter
        self.setParent(parent)

    def set_parameter(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        self.parameter.value = data