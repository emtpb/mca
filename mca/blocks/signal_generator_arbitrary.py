import json

import numpy as np

from mca import exceptions
from mca.framework import Block, data_types, parameters
from mca.language import _


class SignalGeneratorArbitrary(Block):
    """Loads arbitrary data to generate a signal on its output."""
    name = _("SignalGeneratorArbitrary")
    description = _("Loads arbitrary data to generate a signal on its output.")
    tags = (_("Generating"), _("Loading"))

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["file_name"] = parameters.PathParameter(
                name=_("Arbitrary data path"),
                loading=True,
                file_formats=[".json"]
        )
        self.parameters["load_file"] = parameters.ActionParameter(
                name=_("Load file"),
                function=self.load_file
        )

    def _process(self):
        pass

    def load_file(self):
        """Loads the arbitrary data from the given file_name to the output."""
        # Read parameters values
        file_name = self.parameters["file_name"].value
        # Verify that the file ends with .json
        if file_name and not file_name.endswith(".json"):
            raise exceptions.DataLoadingError("Filename has to end with .json")
        # Try loading the signal data
        try:
            with open(file_name, 'r') as arbitrary_file:
                arbitrary_data = json.load(arbitrary_file)
                if arbitrary_data.get("data_type") != "Signal":
                    raise exceptions.DataLoadingError(
                        "Loaded data type is not a signal.")

        except FileNotFoundError:
            raise exceptions.DataLoadingError("File not found")
        # Apply loaded signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=arbitrary_data["abscissa_start"],
            values=arbitrary_data["values"],
            increment=arbitrary_data["increment"],
            ordinate=np.array(arbitrary_data["ordinate"])
        )
        # Apply metadata from the loaded signal
        self.outputs[0].process_metadata = data_types.MetaData(
                    name=arbitrary_data["name"],
                    unit_a=arbitrary_data["unit_a"],
                    unit_o=arbitrary_data["unit_o"],
                    quantity_a=arbitrary_data["quantity_a"],
                    quantity_o=arbitrary_data["quantity_o"],
                    symbol_a=arbitrary_data["symbol_a"],
                    symbol_o=arbitrary_data["symbol_o"],
        )
        # Trigger an update manually since this is not executed within process
        self.trigger_update()
