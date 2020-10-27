import json
import numpy as np

from mca import exceptions
from mca.framework import data_types, parameters, Block
from mca.language import _


class SignalGeneratorArbitrary(Block):
    """Block class which loads arbitrary data to generate a signal.

    This block has one output.
    """
    name = _("SignalGeneratorArbitrary")
    description = _("Loads arbitrary data to generate a signal on its output.")
    tags = ("Generating",)

    def __init__(self, **kwargs):
        super().__init__()

        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
            ),
        )
        self.parameters.update({"file": parameters.PathParameter(_("Arbitrary data path"))})
        self.read_kwargs(kwargs)

    def _process(self):
        file_path = self.parameters["file"].value
        if not file_path:
            return
        with open(file_path, 'r') as arbitrary_file:
            arbitrary_data = json.load(arbitrary_file)
            if arbitrary_data.get("data_type") != "Signal":
                raise exceptions.DataLoadingError(
                    "Loaded data type is not a signal.")
            meta_data = data_types.MetaData(
                arbitrary_data["name"],
                arbitrary_data["unit_a"],
                arbitrary_data["unit_o"],
                arbitrary_data["quantity_a"],
                arbitrary_data["quantity_o"],
                arbitrary_data["symbol_a"],
                arbitrary_data["symbol_o"],
                )
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=arbitrary_data["abscissa_start"],
            values=arbitrary_data["values"],
            increment=arbitrary_data["increment"],
            ordinate=np.fromstring(arbitrary_data["ordinate"][1:-1],
                                   sep=" ", dtype=float)
            )
