import numpy as np

from mca.framework import Block, data_types, parameters, util
from mca.language import _


class Impulse(Block):
    """Generates an impulse signal with a pulse height of 1.
    Note that the pulse length and the shift have no units and are related to
    the amount of values which are set by the abscissa parameter.
    """
    name = _("Impulse")
    description = _("Generates an impulse signal. Note that the pulse length "
                    "and the shift have no units and are related to the amount "
                    "of values which are set by the abscissa parameter.")
    tags = (_("Generating"),)

    def setup_io(self):
        self.new_output(user_metadata_required=False)

    def setup_parameters(self):
        self.parameters["pulse_length"] = parameters.IntParameter(
            name=_("Pulse length"), min_=1, max_=None, default=1
        )
        self.parameters["shift"] = parameters.IntParameter(
            name=_("Shift of the pulse on the abscissa"), min_=0, max_=None,
            default=0
        )
        self.parameters["abscissa"] = util.create_abscissa_parameter_block()

    def process(self):
        # Read parameters values
        pulse_length = self.parameters["pulse_length"].value
        shift = self.parameters["shift"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        # Calculate the ordinate
        ordinate = np.zeros(values)
        ordinate[shift: shift+pulse_length] = 1
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
