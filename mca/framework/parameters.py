import logging

from mca import exceptions


class BaseParameter:
    """Base class for parameters in a :class:`.Block`.
    
    Attributes:
        name (str): Name of the parameter.
        unit (str): Unit of the parameter.
    """

    def __init__(self, name, unit=None, default=None):
        """Initialize BaseParameter class.
        
        Args:
            name (str): Name of the parameter.
            unit (str): Unit of the parameter.
            default: Default for the internal value of the parameter.
        """
        self.name = name
        self.unit = unit
        self._value = default
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
        logging.info(f"Changing value of {self.name} from {self._value} "
                     f"to {val}")
        self.validate(val)
        self._value = val
        if self.parameter_block:
            self.parameter_block.update(source=self)


class FloatParameter(BaseParameter):
    """Parameter for float numbers.
    
    Attributes:
        min_ (float): Minimum value of the parameter.
        max_ (float): Maximum value of the parameter.
        default (float): Value of the parameter.
        """

    def __init__(self, name, min_=None, max_=None, unit=None, default=None):
        """Initialize FloatParameter class.
        
        Args:
            name (str): Name of the parameter.
            min_ (float): Minimum value of the parameter.
            max_ (float): Maximum value of the parameter.
            unit (str): Unit of the parameter.
            default (float): Value of the parameter.
        """
        super().__init__(name=name, unit=unit, default=default)
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
        if self.max is not None:
            if value > self.max:
                raise exceptions.OutOfBoundError(self.name)
        if self.min is not None:
            if value < self.min:
                raise exceptions.OutOfBoundError(self.name)


class IntParameter(BaseParameter):
    """Parameter class for integers.
    
    Attributes:
        min (int): Minimum value of the parameter.
        max (int): Maximum value of the parameter.
        default (int): Value of the parameter.
    """

    def __init__(self, name, min_=None, max_=None, unit=None, default=None):
        """Initialize IntParameter class.
        
        Args:
            name (str): Name of the parameter.
            min_ (int): Minimum value of the parameter.
            max_ (int): Maximum value of the parameter.
            unit (str): Unit of the parameter.
            default (int): Value of the parameter.
        """
        super().__init__(name=name, unit=unit, default=default)
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
            raise exceptions.ParameterTypeError(self.name, int, type(value))
        if self.max is not None:
            if value > self.max:
                raise exceptions.OutOfBoundError(self.name)
        if self.min is not None:
            if value < self.min:
                raise exceptions.OutOfBoundError(self.name)

    @property
    def value(self):
        return super().value

    @BaseParameter.value.setter
    def value(self, val):
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        self.validate(val)
        self._value = val
        if self.parameter_block:
            self.parameter_block.update(source=self)


class StrParameter(BaseParameter):
    """Parameter class for strings.
    
    Attributes:
        default (str): Value of the parameter.
        max_length (int): Maximum length of the string.
    """

    def __init__(self, name, max_length=20, default=None):
        """Initialize StrParameter class.
        
        Args:
            name (str): Name of the parameter.
            max_length (int): Maximum length of the string.
            default (str): Value of the parameter.
        """
        super().__init__(name=name, default=default)
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
        default: Value of the parameter.
    """

    def __init__(self, name, choices, unit=None, default=None):
        """Initialize ChoiceParameter class.
        
        Args:
            name (str): Name of the parameter.
            choices: List of different choices which are tuples with a key and
                     a translatable display name.
            unit (str): Unit of the parameter.
            default: Value of the parameter of one of the choices.
        """
        super().__init__(name=name, unit=unit, default=default)
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
        default (bool): Value of the Parameter.
    """

    def __init__(self, name, default=None):
        """Initialize BoolParameter class.
        
        Args:
            name (str): Name of the Parameter.
            default (bool): Value of the Parameter.
        """
        super().__init__(name=name, default=default, )

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
        default: Path of the file.
    """
    def __init__(self, name, file_formats=None, loading=False, default=""):
        """Initialize PathParameter.

        Args:
           name (str): Name of the Parameter.
           default (str): Path to the desired file.
           file_formats (list): List of allowed file formats.
        """
        super().__init__(name, default)
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
    """Conversion class for holding necessary data for a
    parameter conversion.

    Attributes:
        main_parameters (list): Parameter which can be manipulated by the user.
        sub_parameters (list): Parameter which get updated when one of the
                               main_parameters gets updated.
        conversion_func: Function executing the conversion.
    """
    def __init__(self, main_parameters, sub_parameters, conversion_func=None):
        """Initializes ParameterConversion.

        Args:
            main_parameters (list): Parameter which can be manipulated by the
                                    user.
            sub_parameters (list): Parameter which get updated when one of the
                                   main_parameters gets updated.
            conversion_func: Function executing the conversion.
        """
        self.main_parameters = main_parameters
        self.sub_parameters = sub_parameters
        self.conversion_func = conversion_func


class ParameterBlock:
    """ParameterBlock class used for managing a group of parameters which
    are dependent on each other or are in someway connected to other
    parameters. Multiple conversions can be specified to model the behaviour of
    those parameters. Those conversions get invoked when one of the
    main_parameters gets modified.

    Attributes:
        name (str): Name of the ParameterBlock.
        parameters (list): List of the included parameters.
        param_conversions (list): List of specified ParameterConversions.
        conversion_index (int): Current active conversion of the
                                param_conversions.
    """
    def __init__(self, parameters, param_conversions=None, default_conversion=None,
                 name=""):
        """Initialize ParameterBlock.

        Args:
            name (str): Name of the ParameterBlock.
            parameters (dict): Mapping of all included parameters.
            param_conversions (list): List of specified ParameterConversions.
            default_conversion (int): Current active conversion of the
                                      param_conversions.
        """
        self.name = name
        self.parameters = parameters
        for parameter in self.parameters.values():
            parameter.parameter_block = self
        if param_conversions:
            self.param_conversions = param_conversions
        else:
            self.param_conversions = []
        self.conversion_index = default_conversion

    def update(self, source):
        """Executes the current active parameter conversion.

        Args:
            source: Parameter which triggered the update.
        """
        if self.param_conversions:
            conversion = self.param_conversions[self.conversion_index]
            if source in conversion.main_parameters:
                if conversion.conversion_func:
                    conversion.conversion_func()
