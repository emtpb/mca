import numpy as np
import matplotlib.pyplot as plt
import copy

from mca.framework import validator, data_types, parameters, DynamicBlock
from mca.language import _


class ComplexPlot(DynamicBlock):
    """Plots absolute and phase or real and imaginary part of the input
    signal.

    Attributes:
        fig: Figure for plotting data.
        first_axes: Reference of the axes for the real part of the input signal.
        second_axes: Reference of the axes for the imaginary part of the
                    input signal.
        legend: Reference of the legend.
    """
    name = _("ComplexPlot")
    description = _("Plots absolute and phase or real and imaginary part of "
                    "the input signal.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes ComplexPlot class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.first_axes = self.fig.add_subplot(211)
        self.second_axes = self.fig.add_subplot(212)
        self.first_axes.grid(True)
        self.second_axes.grid(True)
        self.legend = None

    def setup_parameters(self):
        self.parameters.update({
            "plot_type": parameters.ChoiceParameter(_("Plot type"), choices=(
                ("real_imag", _("Real/Imaginary")),
                ("abs_phase", _("Absolute/Phase"))),
                                                    default="abs_phase"),
            "show": parameters.ActionParameter(_("Show plot"), self.show,
                                               display_options=("block_button",
                                                                "edit_window")),
            "auto_show": parameters.BoolParameter(_("Auto plot"), False),
        })

    def setup_io(self):
        self.dynamic_input = [1, None]
        self.new_input()

    def _process(self):
        self.first_axes.lines.clear()
        self.second_axes.lines.clear()
        if self.legend:
            self.legend.remove()

        for i in self.inputs:
            validator.check_type_signal(i.data)
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        abscissa_units = [signal.metadata.unit_a for signal in signals]
        ordinate_units = [signal.metadata.unit_o for signal in signals]
        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)

        auto_show = self.parameters["auto_show"].value
        plot_type = self.parameters["plot_type"].value
        labels = False

        for signal in signals:
            abscissa = np.linspace(signal.abscissa_start,
                                   signal.abscissa_start + signal.increment * (signal.values - 1),
                                   signal.values)
            ordinate = signal.ordinate
            label = signal.metadata.name
            if label:
                labels = True
            if plot_type == "real_imag":
                self.first_axes.plot(abscissa, ordinate.real, "C0", label=label)
                self.second_axes.plot(abscissa, ordinate.imag, "C0")
            elif plot_type == "abs_phase":
                self.first_axes.plot(abscissa, abs(ordinate), "C0", label=label)
                self.second_axes.plot(abscissa, np.angle(ordinate), "C0")
        if labels:
            self.legend = self.fig.legend()
        else:
            self.legend = None
        if signals:
            metadata = signals[0].metadata
            abscissa_string = data_types.metadata_to_axis_label(
                quantity=metadata.quantity_a,
                unit=metadata.unit_a,
                symbol=metadata.symbol_a
            )
            ordinate_string = data_types.metadata_to_axis_label(
                quantity=metadata.quantity_o,
                unit=metadata.unit_o,
                symbol=metadata.symbol_o
            )
            self.first_axes.set_xlabel(abscissa_string)
            self.first_axes.set_ylabel(ordinate_string)
            self.second_axes.set_xlabel(abscissa_string)
            if plot_type == "abs_phase":
                self.second_axes.set_ylabel(_("Phase in rad"))
            else:
                self.second_axes.set_ylabel(ordinate_string)

        self.fig.tight_layout()
        self.fig.canvas.draw()

        if auto_show:
            self.show()

    def show(self):
        """Shows the plot."""
        self.fig.show()
