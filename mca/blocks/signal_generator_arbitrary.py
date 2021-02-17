import json
import numpy as np

from mca import exceptions
from mca.framework import data_types, parameters, Block
from mca.language import _


class SignalGeneratorArbitrary(Block):
    """Loads arbitrary data to generate a signal.

    This block has one output.
    """
    name = _("SignalGeneratorArbitrary")
    description = _("Loads arbitrary data to generate a signal on its output.")
    tags = (_("Generating"), _("Loading"))

    def __init__(self, **kwargs):
        """Initializes SignalGeneratorArbitrary class."""
        super().__init__()

        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )
        self.parameters.update({
            "file_name": parameters.PathParameter(
                _("Arbitrary data path"),
                loading=True,
                file_formats=[".json"]),
            "load_file": parameters.ActionParameter(
                _("Load file"),
                self.load_file)
        })
        self.read_kwargs(kwargs)

    def _process(self):
        pass

    def load_file(self):
        """Loads the arbitrary data from the given file_name to the output."""
        file_name = self.parameters["file_name"].value
        if not file_name:
            raise exceptions.DataLoadingError("No file given to load.")
        with open(file_name, 'r') as arbitrary_file:
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
        self.update()
