import numpy as np

from mca.framework import data_types, parameters, helpers, Block
from mca.language import _


class SignalGeneratorStochastic(Block):
    """Generates a stochastic signal with either normal or equal
    distribution.
    """
    name = "SignalGeneratorStochastic"
    description = _("Generates a stochastic signal "
                    "with either normal or equal distribution.")
    tags = (_("Generating"), _("Stochastic"))

    def setup_io(self):
        self._new_output(
            meta_data=data_types.default_meta_data(),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )

    def setup_parameters(self):
        abscissa = helpers.create_abscissa_parameter_block()
        self.parameters.update({
            "dist": parameters.ChoiceParameter(
                _("Distribution"),
                choices=[("normal", _("Normal distribution")),
                         ("equal", _("Equal distribution"))],
                value="normal"
            ),
            "mean": parameters.FloatParameter(_("Mean µ"), value=0),
            "std_dev": parameters.FloatParameter(_("Standard deviation σ"),
                                                 min_=0, value=1),
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
            ordinate = mean + std_dev*np.random.randn(values)
        elif dist == "equal":
            ordinate = mean + std_dev * np.sqrt(12) * (np.random.rand(values)-0.5)

        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(None),
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
