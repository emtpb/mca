import numpy as np

from mca.framework import Block, data_types, parameters, util
from mca.language import _


class DCGenerator(Block):
    """Generates a DC signal."""
    name = _("DCGenerator")
    description = _("Generates a DC signal.")
    tags = (_("Generating"),)

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["dc_value"] = parameters.FloatParameter(
            name=_("DC Value"), default=1
        )
        abscissa = util.create_abscissa_parameter_block()
        self.parameters["abscissa"] = abscissa

    def _process(self):
        # Read parameters values
        dc_value = self.parameters["dc_value"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        # Calculate the ordinate
        ordinate = dc_value * np.ones(values)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
