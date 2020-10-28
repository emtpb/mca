"""Validation methods used in mca."""

from mca import exceptions
from mca.framework import data_types


def check_intervals(signals):
    """Check if the values of the signals are compatible for example
    for adding or multiplying.
    
    The abscissa of :class:`~mca.framework.data_types.Signal` is described with
    the starting point, amount of values and the increment. In order to add
    two signals they need to have the same increment 
    and a 'compatible' starting point.
    
    Example: 
        >>> x1 = np.linspace(0, 100, 1)
        >>> x2 = np.linspace(0, 100, 0.5)
        
    Different increments cause incompatibility.
    
    Example:
        >>> x1 = np.linspace(0, 100, 1)
        >>> x2 = np.linspace(0.5, 100.5, 1)
        
    Same increment but the interval points do still not match.
    
    Those intervals are not compatible for summation, multiplication etc.
    
    Example:
        >>> x1 = np.linspace(-10, 100, 1)
        >>> x2 = np.linspace(20, 80, 1)
        
    Those intervals are compatible.
    
    Args:
        signals: List of Signals to be checked.
    
    Raises:
        :class:`.IntervalError`: If intervals are incompatible.
    """
    if signals:
        i = signals[0]
        for signal in signals:
            if signal.increment != i.increment:
                raise exceptions.IntervalError("Increment of two signals "
                                               "are not equal")
            diff = ((
                                i.abscissa_start - signal.abscissa_start) / signal.increment) % 1
            if 0.000001 < diff < 0.9999999:
                raise exceptions.IntervalError("Two signals are incompatible"
                                               "due signal starts")


def check_type_signal(data):
    """Check if the given data is a :class:`.Signal`.

    Args:
        data: Data object to validate.

    Raises:
        :class:`.DataTypeError`: If the given data is not a signal.
    """
    if data:
        if not isinstance(data, data_types.Signal):
            raise exceptions.DataTypeError(data, data_types.Signal)


def check_same_units(units):
    """Check if units are equal.

    Args:
        units (list): Units to compare to each other.
    """
    for unit in units:
        if unit != units[0]:
            raise exceptions.UnitError(unit, units[0])
