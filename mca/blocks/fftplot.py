import matplotlib.pyplot as plt
import numpy as np

import mca.framework
from mca.framework import validator
from mca import exceptions
from mca.language import _


class FFTPlot(mca.framework.Block):
    """Block class which plots the FFT of the input signal.

    This block has one input.

    Parameters:
        shift: No shift, Shift, Shift and only positive frequencies
        plot_mode: Real, Imaginary, Absolute, Phase

    """
    name = "FFTPlot"
    description = _("Computes the FFT of the input signal and plots "
                    "either the real part, imaginary part, "
                    "the absolute or the phase of the FFT. "
                    "Shifts the FFT optionally or cuts the input"
                    "signal before the conversion.")

    def __init__(self, **kwargs):
        super().__init__()

        self._new_input()
        self.parameters = {
            "shift": mca.framework.parameters.ChoiceParameter(
                _("Shift to ordinate"),
                [_("No shift"), _("Shift"),
                 _("Shift and only positive frequencies")],
                value=_("No shift"),
            ),
            "plot_mode": mca.framework.parameters.ChoiceParameter(
                _("Plot Mode"),
                [_("Real"), _("Imaginary"), _("Absolute"), _("Phase")],
                value=_("Absolute"),
            ),
        }
        self.read_kwargs(kwargs)

    def _process(self):
        # Finish when no inputs connected
        if self.check_empty_inputs():
            return

        validator.check_type_signal(self.inputs[0].data)
        # Read parameters
        input_signal = self.inputs[0].data
        plot_mode = self.parameters["plot_mode"].value
        shift = self.parameters["shift"].value
        sample_freq = 1 / self.inputs[0].data.increment
        # Calculate fft
        ordinate = np.fft.fft(input_signal.ordinate)
        values = input_signal.values
        abscissa = np.linspace(0, sample_freq * 2 * np.pi, values)
        # Apply parameters
        if shift == _("Shift") or \
                shift == _("Shift and only positive frequencies"):
            ordinate = np.fft.fftshift(ordinate)
        if shift == _("Shift"):
            abscissa = np.linspace(-sample_freq * np.pi,
                                 sample_freq * np.pi, values)
        elif shift == _("Shift and only positive frequencies"):
            ordinate = ordinate[len(ordinate) // 2:]
            abscissa = abscissa[len(abscissa) // 2:]
        if plot_mode == _("Real"):
            ordinate = ordinate.real
        elif plot_mode == _("Imaginary"):
            ordinate = ordinate.imag
        elif plot_mode == _("Absolute"):
            ordinate = abs(ordinate)
        elif plot_mode == _("Phase"):
            ordinate = np.angle(ordinate)
        plt.figure(num="FFTPlot")
        plt.plot(abscissa, ordinate)
        plt.xlabel("Freq / Hz")
        plt.grid(True)
