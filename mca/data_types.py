from dataclasses import dataclass
import numpy as np


class Signal:
    """Standard data type of mca.
    
    The class describes a signal with two axes and its meta data. The ordinate
    is stored in a one dimensional numpy array. Since this data type
    only allows equidistant sampled signals the abscissa
    can be described with 3 parameters: starting point (abscissa_start),
    amount of values (values) and the sampling rate (increment).
    
    Attributes:
        meta_data: Meta data of the signal with quantity, symbol and unit
            for abscissa- and ordinate-axis.
        abscissa_start (float): Starting point of the signal.
        values (int): Amount of values the signal contains.
        increment (float): Increment between two values.
        ordinate : Ordinate stored in a numpy_array.
    """

    def __init__(self, meta_data, abscissa_start, values, increment, ordinate):
        """Initialize Signal.
        
        Args:
            meta_data: Meta data of the signal with quantity, symbol and unit
                for abscissa and ordinate.
            abscissa_start (float): Starting point of the signal.
            values (int): Amount of values the signal contains.
            increment (float): Increment between two values.
            ordinate : Ordinate stored in a numpy_array.
        """
        self.meta_data = meta_data
        self.abscissa_start = abscissa_start
        self.values = values
        self.increment = increment
        self.ordinate = ordinate

    def __eq__(self, other):
        """Defines equality of two signals.

        Equality is given if abscissa and ordinate are equal.
        """
        if not isinstance(other, self.__class__):
            return False
        if self.abscissa_start != other.abscissa_start:
            return False
        if self.values != other.values:
            return False
        if self.increment != other.increment:
            return False
        if not np.array_equal(self.ordinate, other.ordinate):
            return False
        return True

@dataclass
class MetaData:
    """Meta data class for the :class:`.Signal` class.

    Attributes:
        name (str): Name of the Signal.
        quantity_a (str): Quantity of the abscissa.
        symbol_a (str): Symbol of the abscissa.
        unit_a (str): Unit for the abscissa.
        quantity_o (str): Quantity of the ordinate.
        symbol_o (str): Symbol of the ordinate.
        unit_o (str): Unit for the ordinate.
    """
    name: str
    quantity_a: str
    symbol_a: str
    unit_a: str
    quantity_o: str
    symbol_o: str
    unit_o: str
