import numpy as np

from mca.framework import data_types, Block, helpers, parameters
from mca.language import _


class DCGenerator(Block):
    """Generates a DC signal."""
    name = _("DCGenerator")
    description = _("Generates a DC signal.")
    tags = (_("Generating"),)

    def setup_io(self):
        self.new_output(
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )

    def setup_parameters(self):
        abscissa = helpers.create_abscissa_parameter_block()
        self.parameters.update({
            "dc_value": parameters.FloatParameter(_("DC Value"), default=1),
            "abscissa": abscissa,
        })

    def _process(self):
        dc_value = self.parameters["dc_value"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        ordinate = dc_value * np.ones(values)
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
