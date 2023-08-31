import numpy as np
from scipy import signal as sgn

from mca.framework import Block, data_types, parameters, util


class SignalGenerator(Block):
    """Generates a rectangle or triangle signal."""
    name = "Signal Generator"
    description = "Generates a rectangle or triangle signal."
    tags = ("Generating",)

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):

        self.parameters["signal_type"] = parameters.ChoiceParameter(
            name="Signal type",
            choices=(("rect", "Rectangle"), ("tri", "Triangle")),
            default="rect"
        )
        self.parameters["width"] = parameters.FloatParameter(
            name="Width", min_=0, default=1
        )
        self.parameters["height"] = parameters.FloatParameter(
            name="Height", min_=0, default=1
        )
        self.parameters["shift"] = parameters.FloatParameter(
            name="Shift", default=0
        )
        abscissa = util.create_abscissa_parameter_block()
        abscissa.parameters["start"].value = -5
        self.parameters["abscissa"] = abscissa

    def process(self):
        # Read parameters values
        height = self.parameters["height"].value
        width = self.parameters["width"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        shift = self.parameters["shift"].value
        signal_type = self.parameters["signal_type"].value
        # Calculate the abscissa
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        # Apply different signal types to calculate the ordinate
        ordinate = np.zeros(values)
        mask = np.logical_and((-width / 2) + shift <= abscissa,
                              abscissa < width / 2 + shift)
        if signal_type == "rect":
            ordinate[mask] = height
        elif signal_type == "tri":
            rect1 = sgn.windows.triang(int(width/increment))
            if mask[-1]:
                ordinate[mask] = rect1[:np.sum(mask)]
            elif mask[0]:
                ordinate[mask] = rect1[np.sum(mask):]
            elif np.sum(mask) == 0:
                pass
            else:
                ordinate[mask] = rect1
            """
            mask1 = np.logical_and((-width/2)+shift < abscissa, abscissa <= shift)
            mask2 = np.logical_and(shift <= abscissa, abscissa < shift+(width/2))
            
            values_per_side = int((width/2)/increment)
            excess_values1 = values_per_side - np.sum(mask1)
            excess_values2 = values_per_side - np.sum(mask2)
            print(excess_values1/values_per_side*height)
            ordinate[mask1] = np.linspace(excess_values1/values_per_side*height,
                                          height, np.sum(mask1))
            ordinate[mask2] = np.linspace(height,
                                          excess_values2/values_per_side*height,
                                          np.sum(mask2))
            """""
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
