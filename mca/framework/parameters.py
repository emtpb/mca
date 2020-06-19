from .. import exceptions


class BaseParameter:
    """Base class for parameters that a :class:`.Block` may contain.
    
    Attributes:
        name (str): Name of the parameter.
        unit (str): Unit of the parameter.
    """

    def __init__(self, name, unit=None):
        """Initialize BaseParameter class.
        
        Args:
            name (str): Name of the parameter.
            unit (str): Unit of the parameter.
        """
        self.name = name
        self.unit = unit

    def validate(self, value):
        raise NotImplementedError


class FloatParameter(BaseParameter):
    """Parameter for float numbers.
    
    Attributes:
        min_ (float): Minimum value of the parameter.
        max_ (float): Maximum value of the parameter.
        value (float): Value of the parameter.
        """

    def __init__(self, name, min_=None, max_=None, unit=None, value=None):
        """Initialize FloatParameter class.
        
        Args:
            name (str): Name of the parameter.
            min_ (float): Minimum value of the parameter.
            max_ (float): Maximum value of the parameter.
            unit (str): Unit of the parameter.
            value (float): Value of the parameter.
        """
        super().__init__(name, unit)
        self.min = min_
        self.max = max_
        if value:
            self.validate(value)
        self.value = value

    def validate(self, value):
        """Validates a value on type and if min max boundaries are 
        followed.
        
        Args:
            value: Given value to be validated.
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not
                                                         float.
            :obj:`~mca.exceptions.OutOfBoundError`: Value is not within min 
            or max.
        """
        if not isinstance(value, float) and not isinstance(value, int):
            raise exceptions.ParameterTypeError(self.name)
        if self.max:
            if value > self.max:
                raise exceptions.OutOfBoundError(self.name)
        if self.min:
            if value < self.min:
                raise exceptions.OutOfBoundError(self.name)


class IntParameter(BaseParameter):
    """Parameter class for integer numbers.
    
    Attributes:
        min (int): Minimum value of the parameter.
        max (int): Maximum value of the parameter.
        value (int): Value of the parameter.
    """

    def __init__(self, name, min_=None, max_=None, unit=None, value=None):
        """Initialize IntParameter class.
        
        Args:
            name (str): Name of the parameter.
            min_ (int): Minimum value of the parameter.
            max_ (int): Maximum value of the parameter.
            unit (str): Unit of the parameter.
            value (int): Value of the parameter.
        """
        super().__init__(name, unit)
        self.min = min_
        self.max = max_
        if value:
            self.validate(value)
        self.value = value

    def validate(self, value):
        """Validates a value on type and if min max boundaries are 
        followed.
        
        Args:
            value: Given value to be validated.
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not
                                                         int.
            :class:`~mca.exceptions.OutOfBoundError`: Value is not within min 
            or max.
        """
        if not isinstance(value, int):
            raise exceptions.ParameterTypeError(self.name)
        if self.max:
            if value > self.max:
                raise exceptions.OutOfBoundError(self.name)
        if self.min:
            if value < self.min:
                raise exceptions.OutOfBoundError(self.name)


class StrParameter(BaseParameter):
    """Parameter class for strings.
    
    Attributes:
        value (str): Value of the parameter.
        max_length (int): Maximum length of the string.
    """

    def __init__(self, name, max_length=20, value=None):
        """Initialize StrParameter class.
        
        Args:
            name (str): Name of the parameter.
            max_length (int): Maximum length of the string.
            value (str): Value of the parameter.
        """
        super().__init__(name)
        self.max_length = max_length
        if value:
            self.validate(value)
        self.value = value

    def validate(self, value):
        """Validates a value on type and if maximum of character length is
        reached.
        
        Args:
            value: Given value to be validated.            
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not
                                                         str.
            :class:`~mca.exceptions.OutOfBoundError`: String is too long.
        """
        if not isinstance(value, str):
            raise exceptions.ParameterTypeError(self.name)
        if self.max_length < len(value):
            raise exceptions.OutOfBoundError(self.name)


class ChoiceParameter(BaseParameter):
    """Parameter class for set amount of choices defined beforehand.
    
    Attributes:
        name (str): Name of the parameter.
        choices: List of options for the value.
        value: Value of the parameter.
    """

    def __init__(self, name, choices, unit=None, value=None):
        """Initialize ChoiceParameter class.
        
        Args:
            name (str): Name of the parameter.
            choices: List of different choices which are tuples with a key and a translatable display name.
            unit (str): Unit of the parameter.
            value: Value of the parameter of one of the choices.
        """
        super().__init__(name, unit)
        self.choices = choices
        if value:
            self.validate(value)
        self.value = value

    def validate(self, value):
        """Validates a value on type and if maximum of character length is
        reached.
        
        Args:
            value: Given value to be validated.            
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not str.
            :class:`~mca.exceptions.OutOfBoundError`: String is too long.
        """
        if value not in [i[0] for i in self.choices]:
            raise exceptions.ParameterTypeError(self.name)


class BoolParameter(BaseParameter):
    """Parameter class for bools.
    
    Args:
        name (str): Name of the Parameter.
        value (bool): Value of the Parameter.
    """

    def __init__(self, name, value=None):
        """Initialize BoolParameter class.
        
        Args:
            name (str): Name of the Parameter.
            value (bool): Value of the Parameter.
        """
        super().__init__(name)
        if value:
            self.validate(value)
        self.value = value

    def validate(self, value):
        """Validates a value on bool type.
    
        Args:
            value: Given value to be validated.
            Raises:
                :class:`~mca.exceptions.ParameterTypeError`: 
                Type of value is not bool.
        """
        if not isinstance(value, bool):
            raise exceptions.ParameterTypeError(self.name)
