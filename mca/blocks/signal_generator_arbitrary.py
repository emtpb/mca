import json

import numpy as np

from mca import exceptions
from mca.framework import data_types, parameters, Block
from mca.language import _


class SignalGeneratorArbitrary(Block):
    """Loads arbitrary data to generate a signal on its output."""
    name = _("SignalGeneratorArbitrary")
    description = _("Loads arbitrary data to generate a signal on its output.")
    tags = (_("Generating"), _("Loading"))

    def setup_io(self):
        self.new_output(
            metadata_input_dependent=False,
            ordinate_metadata=False,
            abscissa_metadata=False,
        )

    def setup_parameters(self):
        self.parameters.update({
            "file_name": parameters.PathParameter(
                _("Arbitrary data path"),
                loading=True,
                file_formats=[".json"]),
            "loadfile": parameters.ActionParameter(
                _("Load file"),
                self.load_file)
        })

    def _process(self):
        pass

    def load_file(self):
        """Loads the arbitrary data from the given file_name to the output."""
        file_name = self.parameters["file_name"].value
        if file_name and not file_name.endswith(".json"):
            raise exceptions.DataLoadingError("Filename has to end with .json")
        try:
            with open(file_name, 'r') as arbitrary_file:
                arbitrary_data = json.load(arbitrary_file)
                if arbitrary_data.get("data_type") != "Signal":
                    raise exceptions.DataLoadingError(
                        "Loaded data type is not a signal.")
                metadata = data_types.MetaData(
                    arbitrary_data["name"],
                    arbitrary_data["unit_a"],
                    arbitrary_data["unit_o"],
                    arbitrary_data["quantity_a"],
                    arbitrary_data["quantity_o"],
                    arbitrary_data["symbol_a"],
                    arbitrary_data["symbol_o"],
                )
        except FileNotFoundError:
            raise exceptions.DataLoadingError("File not found")
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(metadata),
            abscissa_start=arbitrary_data["abscissa_start"],
            values=arbitrary_data["values"],
            increment=arbitrary_data["increment"],
            ordinate=np.array(arbitrary_data["ordinate"])
        )
        self.trigger_update()
