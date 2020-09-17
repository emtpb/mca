from PySide2 import QtWidgets, QtCore, QtGui
from united import Unit


class BaseParameterWidget:
    """Basic  parameter widget class for all specific parameter widgets.

    Attributes:
        parameter: Given :class:`.Parameter` to display.
        prev_value: Stores the last value of the parameter until changes get
                    finally applied.
        changed (bool): Indicates whether the current value in the widget
                        differs from the previous value.
    """

    def __init__(self, parameter):
        """Initialize BaseParameterWidget class.

        Args:
            parameter: Given :class:`.Parameter` to display.
        """
        self.parameter = parameter
        self.prev_value = self.parameter.value
        self.changed = False

    def write_parameter(self):
        """Takes the current value in the widget and sets
        it in the parameter.
        """
        raise NotImplementedError

    def read_parameter(self):
        """Reads the current value in the parameter
        and sets it in the widget.
        """
        raise NotImplementedError

    def check_changed(self):
        """Identifies if the value differs from the previous value and
        visually modifies the widget."""
        raise NotImplementedError

    def apply_changes(self):
        """Accepts changes to the parameter."""
        raise NotImplementedError

    def revert_changes(self):
        """Reverts changes made by the user and applies the
        previous parameter again."""
        raise NotImplementedError

    def modified(self):
        """Informs the :class:`.MainWindow` that there are unsaved changes."""
        self.window().parent().modified = True


class FloatParameterWidget(BaseParameterWidget, QtWidgets.QLineEdit):
    """Widget to display a FloatParameter."""

    def __init__(self, parameter):
        """Initialize FloatParameterWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.textChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.changed:
            self.parameter.value = float(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))

    def check_changed(self):
        try:
            float(self.text())
        except ValueError:
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid red;")
            self.changed = True
            return
        if self.parameter.value != float(self.text()):
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = float(self.text())
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        self.setText(str(self.prev_value))
        self.setStyleSheet("")
        self.write_parameter()
        self.read_parameter()
        self.changed = False


class IntParameterWidget(BaseParameterWidget, QtWidgets.QLineEdit):
    """Widget to display a IntParameter."""

    def __init__(self, parameter):
        """Initialize IntParameterWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.textChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.changed:
            self.parameter.value = int(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))

    def check_changed(self):
        try:
            int(self.text())
        except ValueError:
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid red;")
            self.changed = True
            return
        if self.parameter.value != int(self.text()):
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = int(self.text())
        self.setStyleSheet("")
        self.changed = False
        self.modified()

    def revert_changes(self):
        self.setText(str(self.prev_value))
        self.write_parameter()
        self.read_parameter()
        self.changed = False


class ChoiceParameterWidget(BaseParameterWidget, QtWidgets.QComboBox):
    """Widget to display a ChoiceParameter."""

    def __init__(self, parameter):
        """Initialize ChoiceParameterWidget class."""
        QtWidgets.QComboBox.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.currentIndexChanged.connect(self.check_changed)
        for i in range(len(self.parameter.choices)):
            self.addItem(self.parameter.choices[i][1],
                         userData=self.parameter.choices[i][0])

    def write_parameter(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        if self.parameter.value != data:
            self.parameter.value = data

    def read_parameter(self):
        for i in range(len(self.parameter.choices)):
            if self.parameter.choices[i][0] == self.parameter.value:
                self.setCurrentText(self.parameter.choices[i][1])

    def check_changed(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        if self.parameter.value != data:
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        self.prev_value = data
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        index = self.findData(self.prev_value)
        self.setCurrentIndex(index)
        self.setStyleSheet("")
        self.write_parameter()
        self.read_parameter()
        self.changed = False


class StringParameterWidget(BaseParameterWidget, QtWidgets.QLineEdit):
    """Widget to display a StringParameter."""

    def __init__(self, parameter):
        """Initialize StringParameterWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.textChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.parameter.value != self.text():
            self.parameter.value = self.text()
            self.modified()

    def read_parameter(self):
        self.setText(self.parameter.value)

    def check_changed(self):
        if self.parameter.value != self.text():
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = self.text()
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        self.setText(self.prev_value)
        self.setStyleSheet("")
        self.write_parameter()
        self.read_parameter()
        self.changed = False


class BoolParameterWidget(BaseParameterWidget, QtWidgets.QCheckBox):
    """Widget to display a BoolParameter."""

    def __init__(self, parameter):
        """Initialize BoolParameterWidget class."""
        QtWidgets.QCheckBox.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.stateChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.changed:
            self.parameter.value = self.isChecked()

    def read_parameter(self):
        self.setChecked(self.parameter.value)

    def check_changed(self):
        if self.parameter.value != self.isChecked():
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = self.isChecked()
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        self.setChecked(self.prev_value)
        self.setStyleSheet("")
        self.write_parameter()
        self.read_parameter()
        self.changed = False


class MetaDataWidget(QtWidgets.QLineEdit):
    """Widget to display attributes of meta data objects.

    Attributes:
        meta_data: Reference of the :class:`.MetaData` object.
        attr(str): Attribute name of the :class:`.MetaData` object.
        prev_value: Stores the last value of the attribute until changes get
                    finally applied.
        changed (bool): Indicates whether the current value in the widget
                        differs from the previous value.
    """
    def __init__(self, meta_data, attr):
        """Initializes MetaDataWidget class.

        Args:
            meta_data: Reference of the :class:`.MetaData` object.
            attr(str): Attribute name of the :class:`.MetaData` object.
        """
        QtWidgets.QLineEdit.__init__(self)
        self.meta_data = meta_data
        self.attr = attr
        self.changed = False
        self.prev_value = getattr(self.meta_data, self.attr)
        self.textChanged.connect(self.check_changed)

    def write_meta_data_attr(self):
        """Writes the value from the widget to the attribute."""
        if self.changed:
            setattr(self.meta_data, self.attr, self.text())

    def read_meta_data_attr(self):
        """Reads the value from the attribute and sets the widget text
        to it.
        """
        attr = getattr(self.meta_data, self.attr)
        if isinstance(attr, Unit):
            attr = repr(attr)
        self.setText(attr)

    def check_changed(self):
        """Checks whether the value has been changed compared to the
        previous value.
        """
        attr = getattr(self.meta_data, self.attr)
        if isinstance(attr, Unit):
            attr = repr(attr)
        if attr != self.text():
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        """Accepts changes to the attribute."""
        self.changed = False
        self.prev_value = getattr(self.meta_data, self.attr)
        self.setStyleSheet("")
        self.window().parent().modified = True

    def revert_changes(self):
        """Reverts changes made by the user and applies the
        previous attribute again."""
        attr = self.prev_value
        if isinstance(attr, Unit):
            attr = repr(attr)
        self.setText(attr)
        self.setStyleSheet("")
        self.write_meta_data_attr()
        self.read_meta_data_attr()
        self.changed = False
