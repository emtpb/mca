import json

from mca import exceptions
from mca.framework import Block, parameters, util
from mca.language import _


class SignalSaver(Block):
    """Saves the input signal in .json file."""
    name = _("SignalSaver")
    description = _("Saves the input signal in .json file.")
    tags = (_("Saving"),)

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters["file_name"] = parameters.PathParameter(
            name=_("Filename"), file_formats=[".json"]
        )
        self.parameters["save"] = parameters.ActionParameter(
            name=_("Save"), function=self.save_data,
            display_options=("edit_window", "block_button")
        )

    def _process(self):
        pass

    def save_data(self):
        """Saves the input data in .json file."""
        # Raise error when the input has no data to save
        if self.all_inputs_empty():
            raise exceptions.DataSavingError("No data to save.")
        # Read the input data
        signal = self.inputs[0].data
        # Read the input metadata
        metadata = self.inputs[0].metadata
        # Read parameters values
        filename = self.parameters["file_name"].value
        # Verify that the file ends with .json
        if not filename.endswith(".json"):
            raise exceptions.DataSavingError("File has to be a .json.")
        # Save input data and metadata
        with open(filename, 'w') as save_file:
            save_data = {"data_type": "Signal",
                         "name": metadata.name,
                         "quantity_a": metadata.quantity_a,
                         "symbol_a": metadata.symbol_a,
                         "unit_a": repr(metadata.unit_a),
                         "quantity_o": metadata.quantity_o,
                         "symbol_o": metadata.symbol_o,
                         "unit_o": repr(metadata.unit_o),
                         "abscissa_start": signal.abscissa_start,
                         "values": signal.values,
                         "increment": signal.increment,
                         "ordinate": signal.ordinate.tolist()}
            json.dump(save_data, save_file)
