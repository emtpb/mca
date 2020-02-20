"""Custom exception classes used throughout mca."""


class MCAError(Exception):
    """Base class for custom exceptions raised by MCAError
    
    All mca-specific exceptions are derived from this class.
    """

    pass


class BlockCircleError(MCAError):
    """Exception raised when a block detects a circle."""

    def __init__(self, block_name):
        """Initialize BlockCircleError.
        
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
        """Initialize IntervalError.
        
        Args:
            cause: Reason for the IntervalError."""

        super().__init__(cause)


class OutOfBoundError(MCAError):
    """Exception raised when a given parameter is too small or to big 
    than excpected.
    """

    def __init__(self, parameter_name):
        """Initialize OutOfBoundError.
        
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

    def __init__(self, parameter_name):
        """Initialize ParameterTypeError.
        
        Args:
            parameter_name (str): Name of the parameter
                where the error occurred.
        """
        super().__init__(
            "The value given to the parameter '{}' is not the correct type".format(
                parameter_name
            )
        )


class InputOutputError(MCAError):
    """Exception raised when the adding or removing of an input or output
    was not successful.
    """

    def __init__(self, cause):
        """Initialize InputOutputError.
        
        Args:
            cause (str): Reason why the operation was not successful.
        """
        super().__init__(cause)


class ConnectionsError(MCAError):
    """Exception raised when connecting or disconnecting fails."""

    def __init__(self, cause):
        """Initialize ConnectionsError.
        
        Args:
            cause (str): Reason why the connecting or disconnecting failed.
        """
        super().__init__(cause)


class DataTypeError(MCAError):
    """Exception raised when the data type of the data in the input does
    not match with the requirements of the Block."""

    def __init__(self, data, data_type):
        """Initialize DataTypeError.

        Args:
            data: Given data object of the input.
            data_type: Expected data type for the input data.
        """
        super().__init__(
            "Input expected {} but was given {}".format(data_type, data)
        )


class DataSavingError(MCAError):
    """Exception raised when the saving of output data was unsuccessful."""
    def __init__(self, cause):
        """Initialize DataSavingError.

        Args:
            cause (str): Reason why saving was unsuccessful.
        """
        super().__init__(cause)


class DataLoadingError(MCAError):
    """Exception raised when the loading data was unsuccessful."""

    def __init__(self, cause):
        """Initialize DataLoadingError.

        Args:
            cause (str): Reason why loading was unsuccessful.
        """
        super().__init__(cause)
