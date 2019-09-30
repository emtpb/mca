from dataclasses import dataclass


class Signal:
    """Standard data type of mca.
    
    The class describes a signal with two axes and its meta data. The ordinate
    is stored in a one dimensional numpy array. Since this data type
    only allows equidistant sampled signals the abscissa
    can be described with 3 parameters: starting point, amount of values and
    the sampling rate.
    
    Attributes:
        meta_data: Meta data of the signal with quantity, symbol and unit
            for abscissa- and ordinate-axis.
        start_a (float): Starting point of the signal.
        values_a (int): Amount of values the signal contains.
        delta_a (float): Increment between two values.
        ordinate : Ordinate stored in a numpy_array.
    """

    def __init__(self, meta_data, start_a, values_a, delta_a, ordinate):
        """Initialize Signal.
        
        Args:
            meta_data: Meta data of the signal with quantity, symbol and unit
            for abscissa- and ordinate-axis.
            start_a (float): Starting point of the signal.
            values_a (int): Amount of values the signal contains.
            delta_a (float): Increment between two values.
            ordinate : Ordinate stored in a numpy_array.
        """
        self.meta_data = meta_data
        self.start_a = x_start
        self.x_values = x_values
        self.delta_x = delta_x
        self.y = y


@dataclass  #x and y neuer name
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
