import json
import numpy as np

import mca.framework
from mca.language import _


class SignalGeneratorArbitrary(mca.framework.Block):
    """Block class which loads arbitrary data to generate a signal.

    This block has one output.
    """
    name = _("SignalGeneratorArbitrary")
    description = _("Loads arbitrary data to generate a signal on its output.")

    def __init__(self, **kwargs):
        super().__init__()

        self._new_output(
            meta_data=mca.framework.data_types.MetaData(
                "Test", _("Time"), "t", "s", _("Voltage"), "U", "V"
            )
        )
        self.read_kwargs(kwargs)

    def _process(self):
        pass

    def load_data(self, file_name):
        with open(file_name, 'r') as arbitrary_file:
            arbitrary_data = json.load(arbitrary_file)

            meta_data = mca.framework.data_types.MetaData(arbitrary_data["name"],
                                                          arbitrary_data["quantity_a"],
                                                          arbitrary_data["symbol_a"],
                                                          arbitrary_data["unit_a"],
                                                          arbitrary_data["symbol_o"],
                                                          arbitrary_data["quantity_o"],
                                                          arbitrary_data["symbol_o"])
        self.outputs[0].data = mca.framework.data_types.Signal(meta_data=meta_data,
                                                               abscissa_start=arbitrary_data["abscissa_start"],
                                                               values=arbitrary_data["values"],
                                                               increment=arbitrary_data["increment"],
                                                               ordinate=np.fromstring(arbitrary_data["ordinate"][1:-1],
                                                                                      sep=" ", dtype=float)
                                                               )