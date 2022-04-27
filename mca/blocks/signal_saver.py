import json

from mca.framework import validator, Block, parameters
from mca.language import _
from mca import exceptions


class SignalSaver(Block):
    """Saves the input signal in .json file."""
    name = _("SignalSaver")
    description = _("Saves the input signal in .json file.")
    tags = (_("Saving"),)

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({
            "file_name": parameters.PathParameter(_("Filename"),
                                                  file_formats=[".json"]),
            "save": parameters.ActionParameter(_("Save"),
                                               self.save_data, display_options=("edit_window", "block_button"))})

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)

    def save_data(self):
        """Saves the the input data in .json file."""
        if not self.inputs[0].data:
            raise exceptions.DataSavingError("No data to save.")
        signal = self.inputs[0].data
        filename = self.parameters["file_name"].value
        if not filename.endswith(".json"):
            raise exceptions.DataSavingError("File has to be a .json.")
        with open(filename, 'w') as save_file:
            save_data = {"data_type": "Signal",
                         "name": signal.metadata.name,
                         "quantity_a": signal.metadata.quantity_a,
                         "symbol_a": signal.metadata.symbol_a,
                         "unit_a": repr(signal.metadata.unit_a),
                         "quantity_o": signal.metadata.quantity_o,
                         "symbol_o": signal.metadata.symbol_o,
                         "unit_o": repr(signal.metadata.unit_o),
                         "abscissa_start": signal.abscissa_start,
                         "values": signal.values,
                         "increment": signal.increment,
                         "ordinate": signal.ordinate.tolist()}
            json.dump(save_data, save_file)
