import matplotlib.pyplot as plt
import numpy as np

from mca.framework import validator, data_types, parameters, Block
from mca.language import _


class Histogramm(Block):
    """Plots absolute and relative frequency of occurrences of
    values in a histogramm.
    """
    name = _("Histogramm")
    description = _("Plots absolute and relative frequency of occurrences of "
                    "values in a histogramm.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes Histogramm class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.legend = None

    def setup_parameters(self):
        self.parameters.update({
            "plot_type": parameters.ChoiceParameter(_("Plot type"), choices=(
                ("absolute", _("Absolute")),
                ("relative", _("Relative")),
                ("density", _("Relative (density)"))
            ),
                                                    default="absolute"),
            "bins": parameters.IntParameter(_("Bins"), min_=1, default=100),
            "show": parameters.ActionParameter(_("Show plot"), self.show,
                                               display_options=("block_button",
                                                                "edit_window")),
            "auto_show": parameters.BoolParameter(_("Auto plot"), False),
        })

    def setup_io(self):
        self.new_input()

    def _process(self):
        self.axes.cla()

        if self.legend:
            self.legend.remove()
            self.legend = None

        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return
        signal = self.inputs[0].data
        validator.check_type_signal(signal)

        auto_show = self.parameters["auto_show"].value
        plot_type = self.parameters["plot_type"].value
        bins = self.parameters["bins"].value

        if plot_type == "absolute":
            density = False
            y_label = _("Absolute frequency of occurrence")
        elif plot_type == "relative":
            density = False
            y_label = _("Relative frequency of occurrence")
        else:
            density = True
            y_label = _("Relative density frequency of occurrence")

        label = signal.metadata.name
        if plot_type == "relative":
            self.axes.hist(signal.ordinate,
                           weights=np.ones(signal.ordinate.shape)/len(signal.ordinate),
                           bins=bins,
                           label=label)
        else:
            self.axes.hist(signal.ordinate, bins=bins, density=density,
                           label=label)

        if label:
            self.legend = self.fig.legend()
        metadata = signal.metadata
        ordinate_string = data_types.metadata_to_axis_label(
            quantity=metadata.quantity_o,
            unit=metadata.unit_o,
            symbol=metadata.symbol_o
        )
        self.axes.set_ylabel(y_label)
        self.axes.set_xlabel(ordinate_string)

        self.axes.grid(True)

        self.fig.tight_layout()
        self.fig.canvas.draw()

        if auto_show:
            self.show()

    def show(self):
        """Shows the plot."""
        self.fig.show()
