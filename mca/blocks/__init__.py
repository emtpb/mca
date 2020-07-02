import sys
import inspect

from .fft import FFT
from .signal_plot import SignalPlot
from .real_imag import RealImag
from .fftplot import FFTPlot
from .signal_generator_periodic import SignalGeneratorPeriodic
from .adder import Adder
from .absolute import Absolute
from .signal_generator_arbitrary import SignalGeneratorArbitrary

block_classes = [i[1] for i in inspect.getmembers(sys.modules[__name__],
                                                  inspect.isclass)]
