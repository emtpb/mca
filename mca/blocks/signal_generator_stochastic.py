import numpy as np

from mca.framework import data_types, parameters, util, Block
from mca.language import _


class SignalGeneratorStochastic(Block):
    """Generates a stochastic signal with either normal or equal
    distribution.
    """
    name = _("SignalGeneratorStochastic")
    description = _("Generates a stochastic signal "
                    "with either normal or equal distribution.")
    tags = (_("Generating"), _("Stochastic"))

    def setup_io(self):
        self.new_output(
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )

    def setup_parameters(self):
        abscissa = util.create_abscissa_parameter_block()
        self.parameters.update({
            "dist": parameters.ChoiceParameter(
                _("Distribution"),
                choices=[("normal", _("Normal distribution")),
                         ("uniform", _("Uniform distribution"))],
                default="normal"
            ),
            "mean": parameters.FloatParameter(_("Mean µ"), default=0),
            "std_dev": parameters.FloatParameter(_("Standard deviation σ"),
                                                 min_=0, default=1),
            "abscissa": abscissa
        })

    def _process(self):
        mean = self.parameters["mean"].value
        std_dev = self.parameters["std_dev"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        dist = self.parameters["dist"].value

        if dist == "normal":
            ordinate = mean + std_dev * np.random.randn(values)
        elif dist == "uniform":
            ordinate = mean + std_dev * np.sqrt(12) * (
                        np.random.rand(values) - 0.5)

        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
