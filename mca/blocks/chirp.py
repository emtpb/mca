import numpy as np
from scipy import signal as sgn

from mca.framework import Block, data_types, parameters, util
from mca.language import _


class Chirp(Block):
    """Generates a chirp signal."""
    name = _("Chirp")
    description = _("Generates a chirp signal. Two frequencies have to be "
                    "specified where the first frequency corresponds to the "
                    "frequency at the beginning of the signal and second "
                    "frequency corresponds to the frequency at the end of the "
                    "signal.")
    tags = (_("Generating"),)

    def setup_io(self):
        self.new_output(
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )

    def setup_parameters(self):

        self.parameters["sweep_kind"]= parameters.ChoiceParameter(
                name=_("Sweep Kind"),
                choices=[("linear", _("Linear")), ("quadratic", _("Quadratic")),
                         ("logarithmic", _("Logarithmic")),
                         ("hyperbolic", _("Hyperbolic"))],
                default="linear"
        )
        self.parameters["freq1"] = parameters.FloatParameter(
            name=_("Start Frequency"), unit="Hz", min_=0, default=1
        )
        self.parameters["freq2"] = parameters.FloatParameter(
            name=_("End Frequency"), unit="Hz", min_=0, default=10
        )
        self.parameters["amp"] = parameters.FloatParameter(
            name=_("Amplitude"), min_=0, default=1
        )
        self.parameters["phase"] = parameters.FloatParameter(
            name=_("Phase"), default=0, unit="°"
        )
        abscissa = util.create_abscissa_parameter_block()
        self.parameters["abscissa"] = abscissa

    def _process(self):
        # Read parameters values
        amp = self.parameters["amp"].value
        freq1 = self.parameters["freq1"].value
        freq2 = self.parameters["freq2"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        phase = self.parameters["phase"].value
        sweep_kind = self.parameters["sweep_kind"].value
        # Create the abscissa vector
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        # Calculate the ordinate
        chirp = amp * sgn.chirp(t=abscissa, f0=freq1, t1=abscissa[-1], f1=freq2,
                                phi=phase, method=sweep_kind)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start,
            values,
            increment,
            chirp,
        )
