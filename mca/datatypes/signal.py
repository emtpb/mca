"""Currently the main class to pack up data made by blocks."""


class Signal:
    """Signal class of mca.
    
    To fully describe a signal there a several parameters needed.
    All Signals have a unit for x- and y-axis to be able 
    to plot it with these units. More important are 
    the (x,y) points to describe the signal. X and Y are
    stored in 2 seperate :ref:`onedimensional numpy  arrays 
    <numpy:arrays.ndarray>` though the X array is here described with only 
    3 parameters (starting point, amount of values and increment) which 
    can be converted to a numpy array again.
    
    Attributes:
        x_description: `namedtuple <https://docs.python.org/3/library/collections.html?highlight=namedtuple#collections.namedtuple>`_
            with quantity, symbol and unit for x-axis.
        y_description: `namedtuple <https://docs.python.org/3/library/collections.html?highlight=namedtuple#collections.namedtuple>`_
            with quantity, symbol and unit for y-axis.
        x_start (float): Starting point of the signal.
        x_values (int): Amount of values the signal contains.
        delta_x (float): Increment between two x values.
        y : y values stored in a numpyarray. 
    """

    def __init__(
        self, name, x_description, y_description, x_start, x_values, delta_x, y
    ):
        """Initialize Signal.
        
        Args:
            name (str): Name of signal
            x_description: namedtuple with unit, symbol and quantity for x-axis
            y_description: namedtuple with unit, symbol and quantity for y-axis
            x_start (float): Starting point of the signal.
            x_values (int): Amount of values x-interval contains.
            delta_x (float): Increment of the x-axis.
            y : y values stored in a numpyarray.   
        """
        self.name = name
        self.x_description = x_description
        self.y_description = y_description
        self.x_start = x_start
        self.x_values = x_values
        self.delta_x = delta_x
        self.y = y
