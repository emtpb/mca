import numpy as np

from mca.framework import validator, data_types, Block
from mca.language import _
from mca import exceptions


class RealToComplex(Block):
    """Combines two real signals into a complex signal. The signal of the
    first input turns into the real part of the output signal and the signal of
    the second input turns into the imaginary part of output signal.
    """
    name = _("RealToComplex")
    description = _("Combines two real signals into a complex signal."
                    " The signal of the first input turns into the real part "
                    "of the output signal and the signal of the second input "
                    "turns into the imaginary part of output signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input(name=_("Real part"))
        self.new_input(name=_("Imaginary part"))

    def setup_parameters(self):
        pass

    def _process(self):
        if self.any_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)
        validator.check_type_signal(self.inputs[1].data)

        real_part = self.inputs[0].data
        imaginary_part = self.inputs[1].data

        validator.check_same_units((real_part.metadata.unit_a,
                                    imaginary_part.metadata.unit_a))
        validator.check_same_units((real_part.metadata.unit_o,
                                    imaginary_part.metadata.unit_o))

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
        ordinate = real_part.ordinate + 1j*imaginary_part.ordinate
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(real_part.metadata),
            abscissa_start=real_part.abscissa_start,
            values=real_part.values,
            increment=real_part.increment,
            ordinate=ordinate,
        )
