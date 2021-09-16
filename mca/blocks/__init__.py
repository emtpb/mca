import sys
import inspect

from .fft import FFT
from .signal_plot import SignalPlot
from .complex_to_real import ComplexToReal
from .real_to_complex import RealToComplex
from .fftplot import FFTPlot
from .signal_generator_periodic import SignalGeneratorPeriodic
from .adder import Adder
from .absolute import Absolute
from .signal_generator_arbitrary import SignalGeneratorArbitrary
from .signal_saver import SignalSaver
from .audio_loader import AudioLoader
from .audio_saver import AudioSaver
from .audio_recorder import AudioRecorder
from .audio_player import AudioPlayer
from .amplifier import Amplifier
from .signal_generator_stochastic import SignalGeneratorStochastic
from .hs_oscilloscope import HSOscilloscope
from .acf import AutoCorrelation
from .ccf import CrossCorrelation
from .psd import PowerDensitySpectrum
from .cpsd import CrossPowerDensitySpectrum
from .complex_plot import ComplexPlot
from .multiplier import Multiplier
from .window import Window
from .chirp import Chirp
from .zerofill import Zerofill
from .gausspulse import GaussPulse
from .differentiator import Differentiator
from .integrator import Integrator
from .divider import Divider
from .envelope import Envelope
from .analytical_signal import AnalyticalSignal
from .limiter import Limiter
from .cutter import Cutter
from .quantization import Quantization
from .iir_filter import IRRFilter
from .resample import Resample
# Create list of
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
