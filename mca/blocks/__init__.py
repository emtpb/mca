import inspect
import sys

from .absolute import Absolute
from .acf import AutoCorrelation
from .adder import Adder
from .amplifier import Amplifier
from .analytical_signal import AnalyticalSignal
from .audio_loader import AudioLoader
from .audio_player import AudioPlayer
from .audio_recorder import AudioRecorder
from .audio_saver import AudioSaver
from .ccf import CrossCorrelation
from .chirp import Chirp
from .complex_plot import ComplexPlot
from .complex_to_real import ComplexToReal
from .convolution import Convolution
from .cps import CrossPowerSpectrum
from .cutter import Cutter
from .dc_generator import DCGenerator
from .differentiator import Differentiator
from .divider import Divider
from .envelope import Envelope
from .fft import FFT
from .fftplot import FFTPlot
from .fft_shift import FFTShift
from .gausspulse import GaussPulse
from .histogramm import Histogramm
from .hs_oscilloscope import HSOscilloscope
from .iir_filter import IRRFilter
from .impulse import Impulse
from .integrator import Integrator
from .interpolate import Interpolate
from .limiter import Limiter
from .multiplier import Multiplier
from .normalization import Normalization
from .plot import Plot
from .polynom_function_generator import PolynomGenerator
from .power_spectrum import PowerSpectrum
from .quantization import Quantization
from .real_to_complex import RealToComplex
from .resample import Resample
from .signal_loader import SignalLoader
from .signal_generator import SignalGenerator
from .signal_generator_periodic import SignalGeneratorPeriodic
from .signal_generator_stochastic import SignalGeneratorStochastic
from .signal_saver import SignalSaver
from .stft_plot import STFTPlot
from .window import Window
from .xy_plot import XYPlot
from .zerofill import Zerofill

# Create list of all blocks
block_classes = [i[1] for i in inspect.getmembers(sys.modules[__name__],
                                                  inspect.isclass)]
block_classes.sort(key=lambda x: x.name)

tags = set()

# Extract all tags
for block_class in block_classes:
    tags.update(block_class.tags)

tags = list(tags)
tags.sort()

# Map tags to a list of blocks possessing the according tag
tag_dict = {tag: [block_class for block_class in block_classes
                  if tag in block_class.tags] for tag in tags}
