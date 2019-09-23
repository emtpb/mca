"""Validation methods used in mca."""

from . import exceptions


def check_intervals(signals):
    """Checks if the X coordinates of the signals are compatible for example
    for adding or multiplying.
    
    X coordinates of :class:`~mca.DataTypes.signal.Signal` are described with 
    the starting point, amount of points and the increment. In order to add
    two signals they need to have the same increment 
    and a fitting starting point.
    
    Example: 
        >>> x1 = np.linspace(0, 100, 1)
        >>> x2 = np.linspace(0, 100, 0.5)
        
    Different increments cause incompatiblility.
    
    Example:
        >>> x1 = np.linspace(0, 100, 1)
        >>> x2 = np.linspace(0.5, 100.5, 1)
        
    Same increment but the interval points do still not match.
    
    Those intervals are not compatible for summation, multiplaction etc.
    
    Example:
        >>> x1 = np.linspace(-10, 100, 1)
        >>> x2 = np.linspace(20, 80, 1)
        
    Those intervals are compatible.
    
    Args:
        signals: List of :class:`~mca.DataTypes.signal.Signal` to be 
            checked.
    
    Raises:
        :obj:`ValueError`: If an empty list is given.
        :class:`.IntervalError`: If intervals are incomaptible.
    """
    if signals:
        i = signals[0]
        for signal in signals:
            if signal.delta_x != i.delta_x:
                raise exceptions.IntervalError
            diff = ((i.x_start - signal.x_start) / signal.delta_x) % 1
            if 0.000001 < diff < 0.9999999:
                raise exceptions.IntervalError
    else:
        raise ValueError("No signals given")
