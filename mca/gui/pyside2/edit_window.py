from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.framework import parameters, DynamicBlock
from mca.gui.pyside2 import edit_widgets
from mca.language import _

widget_dict = {parameters.BoolParameter: edit_widgets.BoolParameterWidget,
               parameters.IntParameter: edit_widgets.IntParameterWidget,
               parameters.FloatParameter: edit_widgets.FloatParameterWidget,
               parameters.ChoiceParameter: edit_widgets.ChoiceParameterWidget,
               parameters.StrParameter: edit_widgets.StringParameterWidget,
               parameters.ActionParameter: edit_widgets.ActionParameterWidget,
               parameters.PathParameter: edit_widgets.FileParameterWidget}


class EditWindow(QtWidgets.QDialog):
    """Window to display the parameter and meta data of a :class:`.Block`.

    Attributes:
        block: Reference of the :class:`.Block` instance.
        main_layout: Arranges the tab widget und the buttons.
        parameter_tab: Tab for holding the parameter widgets.
        parameter_layout: Grid layout which arranges the parameter widgets.
        meta_data_tab: Tab for holding the meta data widgets.
        meta_data_layout: Grid layout which arranges the meta data widgets.
        button_box: "Ok|Cancel" button widgets.
    """
    def __init__(self, parent, block):
        """Initialize EditWindow class.

        Args:
            block: Reference of the :class:`.Block` instance.
        """
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.block = block
        self.resize(500, 400)
        self.setMaximumSize(QtCore.QSize(500, 400))
        self.setWindowTitle(_("Edit"))
        # Define font for headline labels in the edit window
        self.headline_font = QtGui.QFont()
        self.headline_font.setFamily("TeXGyreHeros")
        self.headline_font.setPointSize(11)
        self.headline_font.setWeight(75)
        self.headline_font.setBold(True)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.parameter_widgets = []
        self.meta_data_widgets = []

        self.tab_widget = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        # Initialize parameter tab
        self.parameter_tab = QtWidgets.QWidget()
        self.parameter_layout = QtWidgets.QGridLayout(self.parameter_tab)
        parameter_count = len(list(filter(
            lambda x: not isinstance(x, parameters.ActionParameter),
            block.parameters.values())))
        parameters_tab_height = (parameter_count + 2) * 30
        self.parameter_tab.setFixedHeight(parameters_tab_height)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.parameter_tab)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)
        self.tab_widget.addTab(scroll, _("Parameters"))
        self.display_parameters()
        # Initialize meta data tab
        self.meta_data_tab = None
        self.meta_data_layout = None
        self.display_meta_data()
        # Set buttons
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setGeometry(QtCore.QRect(140, 360, 329, 23))
        self.button_box.setContentsMargins(0, 0, 10, 10)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.main_layout.addWidget(self.button_box)
        # Set custom window icon
        if self.block.icon_file:
            icon = QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + self.block.icon_file)
            self.setWindowIcon(icon)
        # Create warning message
        self.warning_message = QtWidgets.QMessageBox()
        self.warning_message.setIcon(QtWidgets.QMessageBox.Warning)
        self.warning_message.setText(
            _("Could not apply the changed parameters and meta data!"
              "Continue editing or revert changes?"))
        self.continue_button = self.warning_message.addButton(
            _("Continue"),
            QtWidgets.QMessageBox.YesRole)
        self.revert_button = self.warning_message.addButton(
            _("Revert"),
            QtWidgets.QMessageBox.NoRole)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("accepted()"),
                               self.apply_changes)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("rejected()"),
                               self.revert_changes)

    def display_parameters(self):
        """Arranges parameters of a block in rows in the window underneath each
        other. One row includes the name of the parameter as a label, the
        desired widget and the unit if given.
        """
        block_parameters = self.block.parameters.values()
        if block_parameters:
            parameter_label = QtWidgets.QLabel(_("Parameters:"),
                                               self.parameter_tab)
            self.parameter_layout.addWidget(parameter_label, 0, 0, 1, 1)
            parameter_label.setFont(self.headline_font)
        for block_parameter, index in zip(block_parameters,
                                          range(1, len(block_parameters) + 1)):
            if not isinstance(block_parameter, parameters.BoolParameter) and \
               not isinstance(block_parameter, parameters.ActionParameter):
                name_label = QtWidgets.QLabel(block_parameter.name)
                self.parameter_layout.addWidget(name_label, index, 0, 1, 1)
            widget = widget_dict[type(block_parameter)](block_parameter)
            self.parameter_widgets.append(widget)
            widget.read_parameter()
            self.parameter_layout.addWidget(widget, index, 1, 1, 1)
            if block_parameter.unit:
                unit_label = QtWidgets.QLabel(block_parameter.unit)
                self.parameter_layout.addWidget(unit_label, index, 2, 1, 1)

    def display_meta_data(self):
        """Arranges the meta data of the outputs of the block in the window."""
        if self.tab_widget.count() == 2:
            self.tab_widget.removeTab(1)
            self.meta_data_widgets = []
        if self.block.outputs:
            self.meta_data_tab = QtWidgets.QWidget()
            self.meta_data_layout = QtWidgets.QGridLayout(self.meta_data_tab)
            meta_data_tab_height = len(self.block.outputs)*300
            self.meta_data_tab.setFixedHeight(meta_data_tab_height)
            self.tab_widget.setCurrentIndex(0)
            scroll = QtWidgets.QScrollArea()
            scroll.setWidget(self.meta_data_tab)
            scroll.setWidgetResizable(True)
            scroll.setFixedHeight(400)
            self.tab_widget.addTab(scroll, _("Meta data"))

        for index, output in enumerate(self.block.outputs):
            if output.name:
                output_label = QtWidgets.QLabel(
                    _("Output '{}' meta data:").format(output.name))
            else:
                output_label = QtWidgets.QLabel(
                    _("Output {} meta data:").format(index))
            output_label.setFont(self.headline_font)
            self.meta_data_layout.addWidget(output_label, index * 10, 0, 1, 1)

            self.meta_data_layout.addWidget(QtWidgets.QLabel(_("Signal name:")),
                                            index * 10 + 1, 0, 1, 1)
            entry_edit_line = edit_widgets.MetaDataEditWidget(
                meta_data=output.meta_data, attr="name"
            )
            entry_edit_line.read_attribute()
            self.meta_data_widgets.append(entry_edit_line)
            self.meta_data_layout.addWidget(entry_edit_line,
                                            index * 10 + 1, 1, 1, 1)

            self.meta_data_layout.addWidget(QtWidgets.QLabel(_("Abscissa quantity:")),
                                            index * 10 + 2, 0, 1, 1)
            entry_edit_line = edit_widgets.MetaDataEditWidget(
                meta_data=output.meta_data, attr="quantity_a"
            )
            entry_edit_line.read_attribute()
            self.meta_data_widgets.append(entry_edit_line)
            self.meta_data_layout.addWidget(entry_edit_line,
                                            index * 10 + 2, 1, 1, 1)

            self.meta_data_layout.addWidget(QtWidgets.QLabel(_("Abscissa symbol:")),
                                            index * 10 + 3, 0, 1, 1)
            entry_edit_line = edit_widgets.MetaDataEditWidget(
                meta_data=output.meta_data, attr="symbol_a"
            )
            entry_edit_line.read_attribute()
            self.meta_data_widgets.append(entry_edit_line)
            self.meta_data_layout.addWidget(entry_edit_line,
                                            index * 10 + 3, 1, 1, 1)

            self.meta_data_layout.addWidget(QtWidgets.QLabel(_("Abscissa unit:")),
                                            index * 10 + 4, 0, 1, 1)
            entry_edit_line = edit_widgets.MetaDataEditWidget(
                meta_data=output.meta_data, attr="unit_a"
            )
            entry_edit_line.read_attribute()
            self.meta_data_widgets.append(entry_edit_line)
            self.meta_data_layout.addWidget(entry_edit_line,
                                            index * 10 + 4, 1, 1, 1)
            abscissa_check_box = edit_widgets.MetaDataBoolWidget(
                _("Use abscissa meta data"), output, "abscissa_meta_data")
            abscissa_check_box.read_attribute()
            if not output.meta_data_input_dependent:
                abscissa_check_box.setEnabled(False)
            self.meta_data_widgets.append(abscissa_check_box)
            self.meta_data_layout.addWidget(abscissa_check_box, index*10+5, 1, 1, 1)
            self.meta_data_layout.addWidget(
                QtWidgets.QLabel(_("Ordinate quantity:")),
                index * 10 + 6, 0, 1, 1)
            entry_edit_line = edit_widgets.MetaDataEditWidget(
                meta_data=output.meta_data, attr="quantity_o"
            )
            entry_edit_line.read_attribute()
            self.meta_data_widgets.append(entry_edit_line)
            self.meta_data_layout.addWidget(entry_edit_line,
                                            index * 10 + 6, 1, 1, 1)
            self.meta_data_layout.addWidget(
                QtWidgets.QLabel(_("Ordinate symbol:")),
                index * 10 + 7, 0, 1, 1)
            entry_edit_line = edit_widgets.MetaDataEditWidget(
                meta_data=output.meta_data, attr="symbol_o"
            )
            entry_edit_line.read_attribute()
            self.meta_data_widgets.append(entry_edit_line)
            self.meta_data_layout.addWidget(entry_edit_line,
                                            index * 10 + 7, 1, 1, 1)

            self.meta_data_layout.addWidget(
                QtWidgets.QLabel(_("Ordinate unit:")),
                index * 10 + 8, 0, 1, 1)
            entry_edit_line = edit_widgets.MetaDataEditWidget(
                meta_data=output.meta_data, attr="unit_o"
            )
            entry_edit_line.read_attribute()
            self.meta_data_widgets.append(entry_edit_line)
            self.meta_data_layout.addWidget(entry_edit_line,
                                            index * 10 + 8, 1, 1, 1)
            ordinate_check_box = edit_widgets.MetaDataBoolWidget(
                _("Use ordinate meta data"), output, "ordinate_meta_data")
            ordinate_check_box.read_attribute()
            if not output.meta_data_input_dependent:
                ordinate_check_box.setEnabled(False)
            self.meta_data_widgets.append(ordinate_check_box)
            self.meta_data_layout.addWidget(ordinate_check_box, index * 10 + 9,
                                            1, 1, 1)

    def apply_changes(self):
        """Tries to apply changes. In case of an error the user gets a
        notification and can choose between reverting his last changes or
        continue editing and potentially fix the error.
        """
        try:
            for parameter_widget in self.parameter_widgets:
                parameter_widget.write_parameter()
            for entry in self.meta_data_widgets:
                entry.write_attribute()
            self.block.trigger_update()
        except Exception:
            self.warning_message.exec_()
            if self.warning_message.clickedButton() == self.revert_button:
                for parameter_widget in self.parameter_widgets:
                    parameter_widget.revert_changes()
                for entry in self.meta_data_widgets:
                    entry.revert_changes()
        else:
            for parameter_widget in self.parameter_widgets:
                parameter_widget.apply_changes()
            for entry in self.meta_data_widgets:
                entry.apply_changes()
            self.accept()

    def revert_changes(self):
        """Revert the last changes made."""
        for parameter_widget in self.parameter_widgets:
            parameter_widget.revert_changes()
        for entry in self.meta_data_widgets:
            entry.revert_changes()
        self.block.trigger_update()
        self.reject()

    def closeEvent(self, e):
        """Event triggered when the close button is pressed."""
        self.apply_changes()

    def show(self):
        if isinstance(self.block, DynamicBlock) and self.block.dynamic_output:
            self.display_meta_data()
        super(EditWindow, self).show()
