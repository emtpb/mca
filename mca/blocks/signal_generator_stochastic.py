import numpy as np

from mca.framework import data_types, parameters, Block
from mca.language import _


class SignalGeneratorStochastic(Block):
    """Generates a stochastic signal with either normal or equal distribution.

    This block has one output.
    """
    name = "SignalGeneratorStochastic"
    description = _("Generates a stochastic signal "
                    "with either normal or equal distribution.")
    tags = (_("Generating"), _("Stochastic"))

    def __init__(self, **kwargs):
        """Initializes SignalGeneratorPeriodic class."""
        super().__init__()

        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
                ),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
            )

        self.parameters.update({
            "dist": parameters.ChoiceParameter(
                _("Distribution"),
                choices=[("normal", _("Normal distribution")),
                         ("equal",  _("Equal distribution"))],
                value="normal"
            ),
            "mean": parameters.FloatParameter(_("Mean µ"), value=0),
            "std_dev": parameters.FloatParameter(_("Standard deviation σ"),
                                                 value=1),
            "start_a": parameters.FloatParameter("Start", value=0),
            "values": parameters.IntParameter(_("Values"), min_=1, value=1000),
            "increment": parameters.FloatParameter(_("Increment"), min_=0,
                                                   value=0.01)
        })
        self.read_kwargs(kwargs)

    def _process(self):
        mean = self.parameters["mean"].value
        std_dev = self.parameters["std_dev"].value
        abscissa_start = self.parameters["start_a"].value
        values = self.parameters["values"].value
        increment = self.parameters["increment"].value
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