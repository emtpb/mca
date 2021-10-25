import numpy as np
from scipy import signal as sgn

from mca.framework import data_types, parameters, helpers,  Block
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
        self._new_output(
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )

    def setup_parameters(self):
        abscissa = helpers.create_abscissa_parameter_block()
        self.parameters.update({
            "sweep_kind": parameters.ChoiceParameter(
                _("Sweep Kind"),
                choices=[("linear", _("Linear")), ("quadratic", _("Quadratic")),
                         ("logarithmic", _("Logarithmic")),
                         ("hyperbolic", _("Hyperbolic"))],
                default="linear"
            ),
            "freq1": parameters.FloatParameter(_("Start Frequency"),
                                               unit="Hz", min_=0, default=1),
            "freq2": parameters.FloatParameter(_("End Frequency"),
                                               unit="Hz", min_=0, default=10),
            "amp": parameters.FloatParameter("Amplitude", min_=0, default=1),
            "phase": parameters.FloatParameter("Phase", default=0, unit="°"),
            "abscissa": abscissa,
        })

    def _process(self):
        amp = self.parameters["amp"].value
        freq1 = self.parameters["freq1"].value
        freq2 = self.parameters["freq2"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        phase = self.parameters["phase"].value
        sweep_kind = self.parameters["sweep_kind"].value
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        chirp = amp * sgn.chirp(t=abscissa, f0=freq1, t1=abscissa[-1], f1=freq2,
                                phi=phase, method=sweep_kind)
        self.outputs[0].data = data_types.Signal(
            self.outputs[0].get_meta_data(None),
            abscissa_start,
            values,
            increment,
            chirp,
        )
