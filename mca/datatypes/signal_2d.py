from dataclasses import dataclass


class Signal:
    """Standard data type of mca.
    
    The class describes a signal with two axes and its meta data. The x-axis
    and the y-axis are stored in one dimensional numpy arrays. Since this
    class only allows signals with a constant sampling rate, the x-axis
    can be described with 3 parameters: starting point, amount of values and
    the sampling rate.
    
    Attributes:
        meta_data: Meta data of the signal with quantity, symbol and unit
            for x- and y-axis.
        x_start (float): Starting point of the signal.
        x_values (int): Amount of values the signal contains.
        delta_x (float): Increment between two x values.
        y : y values stored in a numpy_array.
    """

    def __init__(self, meta_data, x_start, x_values, delta_x, y):
        """Initialize Signal.
        
        Args:
            meta_data: namedtuple with the name of the signal and unit, symbol
                and quantity for x- and y-axis
            x_start (float): Starting point of the signal.
            x_values (int): Amount of values x-interval contains.
            delta_x (float): Increment of the x-axis.
            y : y values stored in a numpy_array.
        """
        self.meta_data = meta_data
        self.x_start = x_start
        self.x_values = x_values
        self.delta_x = delta_x
        self.y = y


@dataclass
class MetaData:
    """Meta data class for the :class:`.Signal` class.

    Attributes:
        name (str): Name of the Signal.
        x_quantity (str): Quantity of the x-axis.
        x_symbol (str): Symbol of the x-axis.
        x_unit (str): Unit for the x-axis.
        y_quantity (str): Quantity of the y-axis.
        y_symbol (str): Symbol of the y-axis.
        y_unit (str): Unit for the y-axis.
    """
    name: str
    x_quantity: str
    x_symbol: str
    x_unit: str
    y_quantity: str
    y_symbol: str
    y_unit: str
