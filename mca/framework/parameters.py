from mca import exceptions


class BaseParameter:
    """Base class for parameters in a :class:`.Block`.
    
    Attributes:
        name (str): Name of the parameter.
        unit (str): Unit of the parameter.
    """

    def __init__(self, name, unit=None, value=None):
        """Initialize BaseParameter class.
        
        Args:
            name (str): Name of the parameter.
            unit (str): Unit of the parameter.
        """
        self.name = name
        self.unit = unit
        self._value = value
        self.parameter_block = None

    def validate(self, value):
        raise NotImplementedError

    @property
    def value(self):
        """Sets or gets the value of the parameter. When setting a value the
        parameter gets validated.

        Args:
            val: Value of the parameter.
        """
        return self._value

    @value.setter
    def value(self, val):
        self.validate(val)
        self._value = val
        if self.parameter_block:
            self.parameter_block.update(source=self)


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
        super().__init__(name=name, unit=unit, value=value)
        self.min = min_
        self.max = max_

    def validate(self, value):
        """Validates a value on type and if its within the min-max boundaries.
        
        Args:
            value: Given value to be validated.
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not
                                                         float.
            :obj:`~mca.exceptions.OutOfBoundError`: Value is not within min 
                                                    or max.
        """
        if not isinstance(value, float) and not isinstance(value, int):
            raise exceptions.ParameterTypeError(self.name, float, type(value))
        if self.max:
            if value > self.max:
                raise exceptions.OutOfBoundError(self.name)
        if self.min:
            if value < self.min:
                raise exceptions.OutOfBoundError(self.name)


class IntParameter(BaseParameter):
    """Parameter class for integers.
    
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
        super().__init__(name=name, unit=unit, value=value)
        self.min = min_
        self.max = max_

    def validate(self, value):
        """Validates a value on type and if the value is within the boundaries.
        
        Args:
            value: Given value to be validated.
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not
                                                         int.
            :class:`~mca.exceptions.OutOfBoundError`: Value is not within min 
                                                      or max.
        """
        if not isinstance(value, int):
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            else:
                raise exceptions.ParameterTypeError(self.name, int, type(value))
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
        super().__init__(name=name, value=value)
        self.max_length = max_length

    def validate(self, value):
        """Validates a value on type and if the value is within the character
        limit.
        
        Args:
            value: Given value to be validated.            
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not
                                                         str.
            :class:`~mca.exceptions.OutOfBoundError`: String is too long.
        """
        if not isinstance(value, str):
            raise exceptions.ParameterTypeError(self.name, str, type(value))
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
            choices: List of different choices which are tuples with a key and
                     a translatable display name.
            unit (str): Unit of the parameter.
            value: Value of the parameter of one of the choices.
        """
        super().__init__(name=name, unit=unit, value=value)
        self.choices = choices

    def validate(self, value):
        """Validates whether the value is in choices.
        
        Args:
            value: Given value to be validated.            
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: value is not in
                                                         choices.
        """
        if value not in [i[0] for i in self.choices]:
            raise exceptions.ParameterValueError(
                "The given value {} is not listed in the choices".format(value)
            )


class BoolParameter(BaseParameter):
    """Parameter class for bools.
    
    Attributes:
        name (str): Name of the Parameter.
        value (bool): Value of the Parameter.
    """

    def __init__(self, name, value=None, parameter_block=None):
        """Initialize BoolParameter class.
        
        Args:
            name (str): Name of the Parameter.
            value (bool): Value of the Parameter.
        """
        super().__init__(name=name, value=value)

    def validate(self, value):
        """Validates a value on bool type.
    
        Args:
            value: Given value to be validated.
            Raises:
                :class:`~mca.exceptions.ParameterTypeError`: 
                Type of value is not bool.
        """
        if not isinstance(value, bool):
            raise exceptions.ParameterTypeError(self.name, bool, type(value))


class ActionParameter(BaseParameter):
    """Parameter class for functions.

    Attributes:
        function: Function this parameter calls.
    """
    def __init__(self, name, function):
        """Initialize ActionParameter.

        Args:
            name (str): Name of the Parameter.
            function: Function this parameter calls.
        """
        super().__init__(name)
        self.function = function

    def validate(self, value):
        pass


class PathParameter(BaseParameter):
    """Parameter class for file paths.

    Attributes:
        value: Path of the file.
    """
    def __init__(self, name, file_formats=None, loading=False, value=""):
        """Initialize PathParameter.

        Args:
           name (str): Name of the Parameter.
           value (str): Path to the desired file.
           file_formats (list): List of allowed file formats.
        """
        super().__init__(name, value)
        if not file_formats:
            file_formats = []
        self.file_formats = file_formats
        self.loading = loading

    def validate(self, value):
        """Validates a value on type and file format.

        Args:
            value: Given value to be validated.
        Raises:
            :class:`~mca.exceptions.ParameterTypeError`: Type of value is not
                                                         str or does not end
                                                         with correct postfix.
        """
        if not isinstance(value, str):
            raise exceptions.ParameterTypeError(self.name, str, type(value))


class ParameterConversion:
    def __init__(self, main_parameters, sub_parameters, conversion_func):
        self.main_parameters = main_parameters
        self.sub_parameters = sub_parameters
        self.conversion_func = conversion_func


class ParameterBlock:
    def __init__(self, parameters, param_conversions, default_conversion):
        self._parameters = parameters
        for parameter in self._parameters:
            parameter.parameter_block = self
        self.param_conversions = param_conversions
        self.conversion_index = default_conversion

    def update(self, source):
        conversion = self.param_conversions[self.conversion_index]
        if source in conversion.main_parameters:
            conversion.conversion_func()

    @property
    def parameters(self):
        current_conversion = self.param_conversions[self.conversion_index]
        return current_conversion.main_parameters

    @property
    def all_parameters(self):
        return self._parameters
