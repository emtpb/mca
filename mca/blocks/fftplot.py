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
        self.parameters.update({
            "shift": mca.framework.parameters.ChoiceParameter(
                _("Shift to ordinate"),
                [("no_shift", _("No shift")), ("shift", _("Shift")),
                 ("shift_positive", _("Shift and only positive frequencies"))],
                value="no_shift",
            ),
            "plot_mode": mca.framework.parameters.ChoiceParameter(
                _("Plot Mode"),
                [("real", _("Real")), ("imaginary", _("Imaginary")),
                 ("absolute", _("Absolute")), ("phase", _("Phase"))],
                value="absolute",
            ),
            "show": mca.framework.parameters.ActionParameter("Show",
                                                             self.show),
            "auto_show": mca.framework.parameters.BoolParameter("Auto plot",
                                                                False)
        })
        self.read_kwargs(kwargs)
        self.fig = plt.figure()

    def _process(self):
        # Close old figure
        plt.close(self.fig)
        # Finish when no inputs connected
        if self.check_empty_inputs():
            return

        validator.check_type_signal(self.inputs[0].data)
        # Read parameters
        input_signal = self.inputs[0].data
        plot_mode = self.parameters["plot_mode"].value
        shift = self.parameters["shift"].value
        auto_show = self.parameters["auto_show"].value
        sample_freq = 1 / self.inputs[0].data.increment
        # Calculate fft
        ordinate = np.fft.fft(input_signal.ordinate)
        values = input_signal.values
        abscissa = np.linspace(0, sample_freq, values)
        # Apply parameters
        if shift == "shift" or \
                shift == "shift_positive":
            ordinate = np.fft.fftshift(ordinate)
        if shift == "shift" or shift == "shift_positive":
            abscissa = np.linspace(-sample_freq / 2,
                                   sample_freq / 2, values)
        if shift == "shift_positive":
            ordinate = ordinate[len(ordinate) // 2:]
            abscissa = abscissa[len(abscissa) // 2:]
        if plot_mode == "real":
            ordinate = ordinate.real
        elif plot_mode == "imaginary":
            ordinate = ordinate.imag
        elif plot_mode == "absolute":
            ordinate = abs(ordinate)
        elif plot_mode == "phase":
            ordinate = np.angle(ordinate)
        self.fig = plt.figure()
        plt.plot(abscissa, ordinate)
        plt.xlabel(mca.framework.data_types.meta_data_to_axis_label(
            quantity=input_signal.meta_data.quantity_a,
            unit=1/input_signal.meta_data.unit_a,
            symbol=input_signal.meta_data.symbol_a
            )
        )
        plt.ylabel(mca.framework.data_types.meta_data_to_axis_label(
            quantity=input_signal.meta_data.quantity_o,
            unit=input_signal.meta_data.unit_o,
            symbol=input_signal.meta_data.symbol_o
            )
        )
        plt.grid(True)
        if auto_show:
            self.fig.show()

    def show(self):
        self.fig.show()
