import collections

"""The main class to pack up data made by blocks."""


class Signal:
    """Signal class of mca.
    
    To fully describe a signal there a several parameters needed.
    All Signals have a unit for x- and y-axis to be able 
    to plot it with these units. More important are 
    the (x,y) points to describe the signal. X and Y are
    stored in 2 separate :ref:`one dimensional numpy  arrays
    <numpy:arrays.ndarray>` though the X array is here described with only
    3 parameters (starting point, amount of values and increment) which 
    can be converted to a numpy array again.
    
    Attributes:
        meta_data: `namedtuple <https://docs.python.org/3/library/collections.html?highlight=namedtuple#collections.namedtuple>`_
            with quantity, symbol and unit for x- and y-axis.
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


meta_data_signal = collections.namedtuple(
    "signal_meta_data",
    [
        "name",
        "x_quantity",
        "x_symbol",
        "x_unit",
        "y_quantity",
        "y_symbol",
        "y_unit",
    ],
)
