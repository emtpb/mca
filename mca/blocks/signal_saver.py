import json

from mca.framework import validator, Block, parameters
from mca.language import _
from mca import exceptions


class SignalSaver(Block):
    """Save the input signal in .json file.

    This block has one input.
    """
    name = _("SignalSaver")
    description = _("Saves the input signal in .json file.")
    tags = (_("Saving"),)

    def __init__(self, **kwargs):
        super().__init__()
        self._new_input()
        self.parameters.update({
            "filename": parameters.PathParameter(_("Filename"),
                                                 file_formats=[".json"]),
            "save": parameters.ActionParameter(_("Save"),
                                               self.save_data)})
        self.read_kwargs(kwargs)

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)

    def save_data(self):
        """Save the the input data in .json file."""
        if not self.inputs[0].data:
            raise exceptions.DataSavingError("No data to save.")
        signal = self.inputs[0].data
        filename = self.parameters["filename"].value
        if not filename.endswith(".json"):
            raise exceptions.DataSavingError("File has to be a .json.")
        with open(filename, 'w') as save_file:
            save_data = {"data_type": "Signal",
                         "name": signal.meta_data.name,
                         "quantity_a": signal.meta_data.quantity_a,
                         "symbol_a": signal.meta_data.symbol_a,
                         "unit_a": repr(signal.meta_data.unit_a),
                         "quantity_o": signal.meta_data.quantity_o,
                         "symbol_o": signal.meta_data.symbol_o,
                         "unit_o": repr(signal.meta_data.unit_o),
                         "abscissa_start": signal.abscissa_start,
                         "values": signal.values,
                         "increment": signal.increment,
                         "ordinate": str(signal.ordinate)}
            json.dump(save_data, save_file)
