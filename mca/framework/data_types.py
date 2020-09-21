from united import Unit
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
        if not np.allclose(self.ordinate, other.ordinate):
            return False
        return True


class MetaData:
    """Meta data class for the :class:`.Signal` class.

    Attributes:
        name (str): Name of the Signal.
        unit_a (Unit): Unit for the abscissa.
        unit_o (Unit): Unit for the ordinate.
        quantity_a (str): Quantity of the abscissa.
        quantity_o (str): Quantity of the ordinate.
        symbol_a (str): Symbol of the abscissa.
        symbol_o (str): Symbol of the ordinate.

    """
    def __init__(self, name, unit_a, unit_o, quantity_a=None, quantity_o=None,
                 symbol_a=None, symbol_o=None):
        """Initialize MetaData.

        Args:
            name (str): Name of the Signal.
            unit_a (Unit): Unit for the abscissa.
            unit_o (Unit): Unit for the ordinate.
            quantity_a (str): Quantity of the abscissa.
            quantity_o (str): Quantity of the ordinate.
            symbol_a (str): Symbol of the abscissa.
            symbol_o (str): Symbol of the ordinate.
        """
        self.name = name
        if isinstance(unit_a, Unit):
            self._unit_a = unit_a
        elif isinstance(unit_a, str):
            self._unit_a = string_to_unit(unit_a)

        if isinstance(unit_o, Unit):
            self._unit_o = unit_o
        elif isinstance(unit_o, str):
            self._unit_o = string_to_unit(unit_o)

        self.quantity_a = quantity_a
        if not self.quantity_a:
            self.quantity_a = self.unit_a.quantity

        self.quantity_o = quantity_o
        if not self.quantity_o:
            self.quantity_o = self.unit_o.quantity

        self.symbol_a = symbol_a
        self.symbol_o = symbol_o

    @property
    def unit_a(self):
        """Gets or sets the abscissa unit. Either a string or a Unit can be
        handed over.
        """
        return self._unit_a

    @unit_a.setter
    def unit_a(self, value):
        if isinstance(value, Unit):
            self._unit_a = value
        elif isinstance(value, str):
            self._unit_a = string_to_unit(value)

    @property
    def unit_o(self):
        """Gets or sets the ordinate unit. Either a string or a Unit can be
        handed over.
        """
        return self._unit_o

    @unit_o.setter
    def unit_o(self, value):
        if isinstance(value, Unit):
            self._unit_o = value
        elif isinstance(value, str):
            self._unit_o = string_to_unit(value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.quantity_a != other.quantity_a:
            return False
        if self.unit_a != other.unit_a:
            return False
        if self.symbol_a != other.symbol_a:
            return False
        if self.quantity_o != other.quantity_o:
            return False
        if self.unit_o != other.unit_o:
            return False
        if self.symbol_o != other.symbol_o:
            return False
        return True


def string_to_unit(string):
    """Converts a string fraction to an Unit object. The string has to be
    in a certain format.

    Example:
         >>> string_1 = "(V*s)/(A*C)"
         >>> string_2 = "V*s"
         >>> string_3 = "1/(A*C)"
         >>> string_4 = "V"

    Args:
        string (str): String to be converted.

    Returns:
        Unit: Converted from the input string.
    """
    string = string.replace("(", "")
    string = string.replace(")", "")
    fraction = string.split("/")
    numerator = None
    denominator = None
    if fraction[0] != 1:
        numerator = fraction[0].split("*")
    if len(fraction) > 1:
        denominator = fraction[1].split("*")
    return Unit(numerator, denominator)


def meta_data_to_axis_label(quantity, unit, symbol=None):
    """Returns a string axis labels given a quantity, unit and (symbol)."""
    if symbol:
        return "{} {} / {}".format(quantity, symbol, unit)
    else:
        return "{} in {}".format(quantity, unit)
