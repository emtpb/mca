from copy import deepcopy
import numpy as np

from mca.framework import validator, data_types, Block, parameters
from mca.language import _


class Normalization(Block):
    """Normalizes input signal by the specified range (By default -1 to 1)."""
    name = _("Normalization")
    description = _("Normalizes input signal by the specified range "
                    "(By default 0-1).")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["min"] = parameters.FloatParameter(name=_("Min"),
                                                           default=0)
        self.parameters["max"] = parameters.FloatParameter(name=_("Max"),
                                                           default=1)

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)
        min_value = self.parameters["min"].value
        max_value = self.parameters["max"].value
        input_signal = self.inputs[0].data
        norm_range = abs(max_value - min_value)
        ordinate = deepcopy(input_signal.ordinate)
        # Normalize between 0 and 1
        normed_ordinate = (ordinate - np.min(ordinate))/np.abs(np.min(ordinate)-np.max(ordinate))
        # Normalize between min and max
        normed_ordinate *= norm_range
        normed_ordinate += min_value

        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(input_signal.metadata),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=normed_ordinate,
        )
