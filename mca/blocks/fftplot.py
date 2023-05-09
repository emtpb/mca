import numpy as np

from mca.framework import PlotBlock, data_types, parameters, util, validator


class FFTPlot(PlotBlock):
    """Plots the FFT of the input signal.

    Attributes:
        fig: Figure for plotting data.
        axes: Reference of the axes.
        legend: Reference of the legend.
    """
    name = "FFTPlot"
    description = ("Computes the FFT of the input signal and plots "
                   "either the real part, imaginary part, "
                   "the absolute or the phase of the FFT. "
                   "Shifts the FFT optionally or cuts the input"
                   "signal before the conversion.")
    tags = ("Processing", "Fouriertransformation", "Plotting")

    def __init__(self, **kwargs):
        """Initializes FFTPlot class."""
        super().__init__(rows=1, cols=1, **kwargs)
        self.legend = None

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters["shift"] = parameters.ChoiceParameter(
                name="Shift to ordinate",
                choices=(("no_shift", "No shift"), ("shift", "Shift"),
                         ("shift_positive",
                          "Shift and only positive frequencies")),
                default="no_shift",
        )
        self.parameters["plot_mode"] = parameters.ChoiceParameter(
                name="Plot Mode",
                choices=(("real", "Real"), ("imaginary", "Imaginary"),
                         ("absolute", "Absolute"), ("phase", "Phase")),
                default="absolute",
        )
        self.parameters["normalize"] = parameters.BoolParameter(
                name="Normalize", default=False
        )

    def setup_plot_parameters(self):
        self.plot_parameters["plot_kind"] = parameters.ChoiceParameter(
                name="Plot kind", choices=(("line", "Line"),
                                              ("stem", "Stem")), )
        self.plot_parameters["color"] = util.get_plt_color_parameter()
        self.plot_parameters["abscissa_scaling"] = parameters.ChoiceParameter(
            name="Abscissa scaling",
            choices=(("linear", "Linear"), ("log", "Log"),
                     ("symlog", "Symmetrcial log"), ("logit", "Logit")),
            default="linear"
        )
        self.plot_parameters["ordinate_scaling"] = parameters.ChoiceParameter(
            name="Ordinate scaling",
            choices=(("linear", "Linear"), ("log", "Log"),
                     ("symlog", "Symmetrcial log"), ("logit", "Logit")),
            default="linear"
        )
        self.plot_parameters["marker"] = util.get_plt_marker_parameter()
        self.plot_parameters["marker_color"] = util.get_plt_color_parameter(
            "Marker color")

    def process(self):
        # Clear the axes and the legend
        self.axes.cla()
        if self.legend:
            self.legend.remove()
            self.legend = None
        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return
        # Validate the input data of type signal
        validator.check_type_signal(self.inputs[0].data)
        # Read the input data
        input_signal = self.inputs[0].data
        # Read the parameters values
        plot_mode = self.parameters["plot_mode"].value
        shift = self.parameters["shift"].value
        normalize = self.parameters["normalize"].value
        # Read plot parameters values
        plot_kind = self.plot_parameters["plot_kind"].value
        abscissa_scaling = self.plot_parameters["abscissa_scaling"].value
        ordinate_scaling = self.plot_parameters["ordinate_scaling"].value
        marker = self.plot_parameters["marker"].value
        color = self.plot_parameters["color"].value
        marker_color = self.plot_parameters["marker_color"].value

        values = input_signal.values
        # Calculate the frequency increment
        delta_f = 1 / (self.inputs[0].data.increment * values)
        # Calculate the ordinate
        ordinate = np.fft.fft(input_signal.ordinate)
        # Normalize the ordinate of needed
        if normalize:
            ordinate = ordinate / values
        # Calculate the absicssa
        abscissa = np.linspace(0, delta_f * (values - 1), values)
        # Shift the ordinate if needed
        if shift == "shift" or \
                shift == "shift_positive":
            ordinate = np.fft.fftshift(ordinate)
        if shift == "shift" or shift == "shift_positive":
            # Recalculate the abscissa
            if values % 2:
                abscissa = np.linspace(-values / 2 * delta_f,
                                       values / 2 * delta_f, values)
            else:
                abscissa = np.linspace(-values / 2 * delta_f,
                                       (values / 2 - 1) * delta_f, values)
        # Cutoff the negative frequencies
        if shift == "shift_positive":
            ordinate = ordinate[len(ordinate) // 2:]
            abscissa = abscissa[len(abscissa) // 2:]
        # The FFT is complex and a plot mode is needed
        if plot_mode == "real":
            ordinate = ordinate.real
        elif plot_mode == "imaginary":
            ordinate = ordinate.imag
        elif plot_mode == "absolute":
            ordinate = abs(ordinate)
        elif plot_mode == "phase":
            ordinate = np.angle(ordinate)

        label = self.inputs[0].metadata.name
        # Plot and pass plot parameters
        if plot_kind == "line":
            self.axes.plot(abscissa, ordinate, color, label=label, marker=marker,
                           markerfacecolor=marker_color,
                           markeredgecolor=marker_color)
        elif plot_kind == "stem":
            self.axes.stem(abscissa, ordinate, color, label=label,
                           use_line_collection=True, basefmt=" ",
                           markerfmt=marker_color+marker)
        if label:
            self.legend = self.fig.legend()
        # Set the x and y labels depending on the metadata of the input
        unit_o = self.inputs[0].metadata.unit_o
        metadata = data_types.MetaData(
            self.inputs[0].metadata.name,
            unit_a=1 / self.inputs[0].metadata.unit_a,
            unit_o=unit_o,
        )
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
        self.axes.set_xscale(abscissa_scaling)
        self.axes.set_yscale(ordinate_scaling)
        # Use grids
        self.axes.grid(True)
        # Draw the plot
        self.fig.canvas.draw()
