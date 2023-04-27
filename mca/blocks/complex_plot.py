import copy

import numpy as np

from mca.framework import DynamicBlock, PlotBlock, data_types, parameters, \
    util, validator
from mca.language import _


class ComplexPlot(DynamicBlock, PlotBlock):
    """Plots absolute and phase or real and imaginary part of the input
    signal.

    Attributes:
        first_axis: Reference of the axes for the real part of the input signal.
        second_axis: Reference of the axes for the imaginary part of the
                    input signal.
        legend: Reference of the legend.
    """
    name = _("ComplexPlot")
    description = _("Plots absolute and phase or real and imaginary part of "
                    "the input signal.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes ComplexPlot class."""
        super().__init__(rows=2, cols=1, **kwargs)
        self.first_axis = self.axes[0]
        self.second_axis = self.axes[1]
        self.legend = None

    def setup_parameters(self):
        self.parameters["plot_type"] = parameters.ChoiceParameter(
            name=_("Plot type"), choices=(("real_imag", _("Real/Imaginary")),
                                          ("abs_phase", _("Absolute/Phase"))),
            default="abs_phase"
        )

    def setup_plot_parameters(self):
        plot_kind = parameters.ChoiceParameter(
            name=_("Plot kind"), choices=[("line", _("Line")),
                                          ("stem", _("Stem"))], )
        abscissa_scaling = parameters.ChoiceParameter(
            name=_("Abscissa scaling"),
            choices=(("linear", _("Linear")), ("log", _("Log")),
                     ("symlog", _("Symmetrcial log")), ("logit", _("Logit"))),
            default="linear"
        )
        ordinate_scaling = parameters.ChoiceParameter(
            name=_("Ordinate scaling"),
            choices=(("linear", _("Linear")), ("log", _("Log")),
                     ("symlog", _("Symmetrcial log")), ("logit", _("Logit"))),
            default="linear"
        )
        color = util.get_plt_color_parameter(_("Color"))
        marker = util.get_plt_marker_parameter()
        marker_color = util.get_plt_color_parameter(_("Marker Color"))
        self.plot_parameters["real_absolute"] = parameters.ParameterBlock(
            name=_("Real/Absolute"),
            parameters={"plot_kind": plot_kind,
                        "abscissa_scaling": abscissa_scaling,
                        "ordinate_scaling": ordinate_scaling,
                        "color": color,
                        "marker": marker,
                        "marker_color": marker_color}
        )
        self.plot_parameters["imag_phase"] = parameters.ParameterBlock(
            name=_("Imag/Phase"),
            parameters={"plot_kind": copy.deepcopy(plot_kind),
                        "abscissa_scaling": copy.deepcopy(abscissa_scaling),
                        "ordinate_scaling": copy.deepcopy(ordinate_scaling),
                        "color": copy.deepcopy(color),
                        "marker": copy.deepcopy(marker),
                        "marker_color": copy.deepcopy(marker_color)}
        )

    def setup_io(self):
        self.dynamic_input = [1, None]
        self.new_input()

    def _process(self):
        # Clear the axes and the legend
        self.first_axis.cla()
        self.second_axis.cla()
        if self.legend:
            self.legend.remove()
        # Validate the input data of type signal
        for i in self.inputs:
            validator.check_type_signal(i.data)
        # Read the input data
        signals = [copy.copy(i.data) for i in self.inputs if i.data]#
        # Read the input metadata
        metadatas = [copy.copy(i.metadata) for i in self.inputs if i.metadata]
        # Read the input metadata units
        abscissa_units = [metadata.unit_a for metadata in metadatas]
        ordinate_units = [metadata.unit_o for metadata in metadatas]
        # Validate the abscissa and ordinate units
        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)
        # Read the parameters values
        plot_type = self.parameters["plot_type"].value
        # Read plot parameters values
        real_absolute_parameters = self.plot_parameters["real_absolute"].parameters
        imag_phase_parameters = self.plot_parameters["imag_phase"].parameters
        plot_kind1 = real_absolute_parameters["plot_kind"].value
        plot_kind2 = imag_phase_parameters["plot_kind"].value
        abscissa_scaling1 = real_absolute_parameters["abscissa_scaling"].value
        ordinate_scaling1 = real_absolute_parameters["ordinate_scaling"].value
        abscissa_scaling2 = imag_phase_parameters["abscissa_scaling"].value
        ordinate_scaling2 = imag_phase_parameters["ordinate_scaling"].value
        color1 = real_absolute_parameters["color"].value
        color2 = imag_phase_parameters["color"].value
        marker1 = real_absolute_parameters["marker"].value
        marker2 = imag_phase_parameters["marker"].value
        marker_color1 = real_absolute_parameters["marker_color"].value
        marker_color2 = imag_phase_parameters["marker_color"].value

        labels_exist = any([metadata.name for metadata in metadatas])
        # Iterate over every signal and its metadata to plot it
        for metadata, signal in zip(metadatas, signals):
            # Create the abscissa vector
            abscissa = np.linspace(signal.abscissa_start,
                                   signal.abscissa_start + signal.increment * (
                                               signal.values - 1),
                                   signal.values)
            ordinate = signal.ordinate
            label = metadata.name
            # Calculate different ordinates depending on the plot type
            if plot_type == "real_imag":
                first_ordinate = ordinate.real
                second_ordinate = ordinate.imag
            elif plot_type == "abs_phase":
                first_ordinate = abs(ordinate)
                second_ordinate = np.angle(ordinate)
            # Plot and pass plot parameters for the first axis
            if plot_kind1 == "line":
                self.first_axis.plot(abscissa, first_ordinate, color1,
                                     label=label, marker=marker1,
                                     markerfacecolor=marker_color1,
                                     markeredgecolor=marker_color1)
            else:
                if marker1 is None:
                    markerfmt1 = None
                else:
                    markerfmt1 = marker_color1 + marker1
                self.first_axis.stem(abscissa, first_ordinate, color1,
                                     label=label, use_line_collection=True,
                                     basefmt=" ", markerfmt=markerfmt1)
            # Plot and pass plot parameters for the second axis
            if plot_kind2 == "line":
                self.second_axis.plot(abscissa, second_ordinate, color2,
                                      label=label, marker=marker2,
                                      markerfacecolor=marker_color2,
                                      markeredgecolor=marker_color2)
            else:
                if marker2 is None:
                    markerfmt2 = None
                else:
                    markerfmt2 = marker_color2 + marker2
                self.second_axis.stem(abscissa, second_ordinate, color2,
                                      label=label, use_line_collection=True,
                                      basefmt=" ", markerfmt=markerfmt2,
                                      )
        # If there are any labels from the metadata then create a legend
        if labels_exist:
            self.legend = self.fig.legend()
        else:
            self.legend = None
        # Set the x and y labels depending on the metadata of the inputs
        if signals:
            metadata = metadatas[0]
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
            self.first_axis.set_xlabel(abscissa_string)
            self.first_axis.set_ylabel(ordinate_string)
            self.second_axis.set_xlabel(abscissa_string)
            if plot_type == "abs_phase":
                self.second_axis.set_ylabel(_("Phase in rad"))
            else:
                self.second_axis.set_ylabel(ordinate_string)
        # Set the scalings
        self.first_axis.set_xscale(abscissa_scaling1)
        self.first_axis.set_yscale(ordinate_scaling1)
        self.second_axis.set_xscale(abscissa_scaling2)
        self.second_axis.set_yscale(ordinate_scaling2)
        # Use grids
        self.first_axis.grid(True)
        self.second_axis.grid(True)
        # Draw the plot
        self.fig.canvas.draw()
