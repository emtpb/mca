import matplotlib.pyplot as plt
import numpy as np

from mca.framework import validator, data_types, Block, parameters
from mca.language import _


class FFTPlot(Block):
    """Plots the FFT of the input signal.

    Attributes:
        fig: Figure for plotting data.
        axes: Reference of the axes.
        legend: Reference of the legend.
    """
    name = _("FFTPlot")
    description = _("Computes the FFT of the input signal and plots "
                    "either the real part, imaginary part, "
                    "the absolute or the phase of the FFT. "
                    "Shifts the FFT optionally or cuts the input"
                    "signal before the conversion.")
    tags = (_("Processing"), _("Fouriertransformation"), _("Plotting"))

    def __init__(self, **kwargs):
        """Initializes FFTPlot class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.legend = None

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({
            "shift": parameters.ChoiceParameter(
                _("Shift to ordinate"),
                [("no_shift", _("No shift")), ("shift", _("Shift")),
                 ("shift_positive", _("Shift and only positive frequencies"))],
                default="no_shift",
            ),
            "plot_mode": parameters.ChoiceParameter(
                _("Plot Mode"),
                [("real", _("Real")), ("imaginary", _("Imaginary")),
                 ("absolute", _("Absolute")), ("phase", _("Phase"))],
                default="absolute",
            ),
            "plot_kind": parameters.ChoiceParameter(
                _("Plot kind"), choices=[("line", _("Line")),
                                         ("stem", _("Stem"))], ),
            "normalize": parameters.BoolParameter(
                _("Normalize"), default=False),
            "show": parameters.ActionParameter("Show plot", self.show,
                                               display_options=(
                                               "block_button",)),
            "auto_show": parameters.BoolParameter("Auto plot", False),
        })

    def _process(self):
        self.axes.cla()
        if self.legend:
            self.legend.remove()
            self.legend = None
        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return
        validator.check_type_signal(self.inputs[0].data)

        input_signal = self.inputs[0].data
        plot_mode = self.parameters["plot_mode"].value
        shift = self.parameters["shift"].value
        auto_show = self.parameters["auto_show"].value
        normalize = self.parameters["normalize"].value
        plot_kind = self.parameters["plot_kind"].value
        values = input_signal.values

        delta_f = 1 / (self.inputs[0].data.increment * values)
        ordinate = np.fft.fft(input_signal.ordinate)
        if normalize:
            ordinate = ordinate / values
        unit_o = input_signal.metadata.unit_o
        abscissa = np.linspace(0, delta_f * (values - 1), values)

        if shift == "shift" or \
                shift == "shift_positive":
            ordinate = np.fft.fftshift(ordinate)
        if shift == "shift" or shift == "shift_positive":
            if values % 2:
                abscissa = np.linspace(-values / 2 * delta_f,
                                       values / 2 * delta_f, values)
            else:
                abscissa = np.linspace(-values / 2 * delta_f,
                                       (values / 2 - 1) * delta_f, values)
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
        metadata = data_types.MetaData(
            input_signal.metadata.name,
            unit_a=1 / input_signal.metadata.unit_a,
            unit_o=unit_o,
        )
        label = input_signal.metadata.name
        if plot_kind == "line":
            self.axes.plot(abscissa, ordinate, "C0", label=label)
        elif plot_kind == "stem":
            self.axes.stem(abscissa, ordinate, "C0", label=label,
                           use_line_collection=True, basefmt=" ")
        if label:
            self.legend = self.fig.legend()

        self.axes.set_xlabel(data_types.metadata_to_axis_label(
            quantity=metadata.quantity_a,
            unit=metadata.unit_a,
            symbol=metadata.symbol_a
        )
        )
        self.axes.set_ylabel(data_types.metadata_to_axis_label(
            quantity=metadata.quantity_o,
            unit=metadata.unit_o,
            symbol=metadata.symbol_o
        )
        )

        self.axes.grid(True)
        self.fig.canvas.draw()

        if auto_show:
            self.show()

    def show(self):
        """Shows the plot."""
        self.fig.show()
