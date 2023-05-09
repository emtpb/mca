import numpy as np

from mca import exceptions
from mca.framework import Block, data_types, util


class RealToComplex(Block):
    """Combines two real signals into a complex signal. The signal of the
    first input turns into the real part of the output signal and the signal of
    the second input turns into the imaginary part of output signal.
    """
    name = "RealToComplex"
    description = ("Combines two real signals into a complex signal. "
                   "The signal of the first input turns into the real part "
                   "of the output signal and the signal of the second input "
                   "turns into the imaginary part of output signal.")
    tags = ("Processing",)

    def setup_io(self):
        self.new_output()
        self.new_input(name="Real part")
        self.new_input(name="Imaginary part")

    def setup_parameters(self):
        pass

    @util.abort_any_inputs_empty
    @util.validate_type_signal
    @util.validate_units(abscissa=True, ordinate=True)
    def process(self):
        # Read the input data
        real_part = self.inputs[0].data
        imaginary_part = self.inputs[1].data
        # Validate the compatibility of the signals
        if real_part.increment != imaginary_part.increment:
            raise exceptions.IntervalError("Real and Imaginary part need to "
                                           "have the same sampling frequency.")
        if real_part.abscissa_start != imaginary_part.abscissa_start:
            raise exceptions.IntervalError("Real and Imaginary part need to "
                                           "have the same abscissa start.")
        if real_part.values != imaginary_part.values:
            raise exceptions.IntervalError("Real and Imaginary part need to "
                                           "have the same amount of sampling "
                                           "values.")
        if np.iscomplex(real_part) or np.iscomplex(imaginary_part):
            raise exceptions.DataTypeError("Input cannot be a complex-valued "
                                           "signal.")
        # Calculate the ordinate
        ordinate = real_part.ordinate + 1j * imaginary_part.ordinate
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=real_part.abscissa_start,
            values=real_part.values,
            increment=real_part.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
