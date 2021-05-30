"""Custom exception classes used throughout mca."""


class MCAError(Exception):
    """Base class for custom exceptions raised by MCAError
    
    All mca-specific exceptions are derived from this class.
    """

    pass


class BlockCircleError(MCAError):
    """Exception raised when a block detects a circle."""

    def __init__(self, block_name):
        """Initializes BlockCircleError.
        
        Args:
            block_name (str): Name of the Block in which 
            the circle was detected.
        """
        super().__init__(
            "In {} was a circle first detected".format(block_name)
        )


class IntervalError(MCAError):
    """Exception raised when there is incompatibility with intervals."""

    def __init__(self, cause):
        """Initializes IntervalError.
        
        Args:
            cause: Reason for the IntervalError."""

        super().__init__(cause)


class OutOfBoundError(MCAError):
    """Exception raised when a value for a parameter is not within its
    boundaries.
    """

    def __init__(self, parameter_name):
        """Initializes OutOfBoundError.
        
        Args:
            parameter_name (str): Name of the parameter 
                where the error occurred.
        """

        super().__init__(
            "The value given to the parameter {} is not in range".format(
                parameter_name
            )
        )


class ParameterTypeError(MCAError):
    """Exception raised when the type of a parameter is not matching."""

    def __init__(self, parameter_name, expected_type, given_type):
        """Initializes ParameterTypeError.
        
        Args:
            parameter_name (str): Name of the parameter
                where the error occurred.
            expected_type: Expected type of the parameter.
            given_type: Given type to the parameter.
        """
        super().__init__(
            "The value given to the parameter '{}' has to be type '{}' not "
            "'{}'".format(parameter_name, expected_type, given_type)
        )


class ParameterValueError(MCAError):
    """Exception raised when a parameter has been handed an invalid value."""

    def __init__(self, cause):
        """Initializes ParameterValueError.

        Args:
            cause (str): Reason why value was invalid.
        """
        super().__init__(cause)


class InputOutputError(MCAError):
    """Exception raised when adding or removing of an input or output
    was unsuccessful.
    """

    def __init__(self, cause):
        """Initializes InputOutputError.
        
        Args:
            cause (str): Reason why the operation was not successful.
        """
        super().__init__(cause)


class ConnectionsError(MCAError):
    """Exception raised when connecting or disconnecting of in- and outputs
    failed.
    """

    def __init__(self, cause):
        """Initializes ConnectionsError.
        
        Args:
            cause (str): Reason why the connecting or disconnecting failed.
        """
        super().__init__(cause)


class DataTypeError(MCAError):
    """Exception raised when the data type of data at the input does
    not match with the requirements of the Block.
    """

    def __init__(self, data, data_type):
        """Initializes DataTypeError.

        Args:
            data: Given data object of the input.
            data_type: Expected data type for the input data.
        """
        super().__init__(
            "Input expected {} but was given {}".format(data_type, data)
        )


class UnitError(MCAError):
    """Exception raised when different units arrive at block which however
    requires equal units.
    """

    def __init__(self, first_unit, second_unit):
        """Initializes UnitError."""
        super().__init__(
            "Conflict with unit {} and {}".format(first_unit, second_unit)
        )


class DataSavingError(MCAError):
    """Exception raised when saving of output data was unsuccessful."""

    def __init__(self, cause):
        """Initializes DataSavingError.

        Args:
            cause (str): Reason why saving was unsuccessful.
        """
        super().__init__(cause)


class DataLoadingError(MCAError):
    """Exception raised when loading data was unsuccessful."""

    def __init__(self, cause):
        """Initializes DataLoadingError.

        Args:
            cause (str): Reason why loading was unsuccessful.
        """
        super().__init__(cause)
