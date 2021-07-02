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
from .signal_saver import SignalSaver
from .audio_loader import AudioLoader
from .audio_saver import AudioSaver
from .audio_recorder import AudioRecorder
from .audio_player import AudioPlayer
from .amplifier import Amplifier
from .signal_generator_stochastic import SignalGeneratorStochastic
from .hs_oscilloscope import HSOscilloscope
from .acf import Autocorrelation

block_classes = [i[1] for i in inspect.getmembers(sys.modules[__name__],
                                                  inspect.isclass)]
tags = set()

for block_class in block_classes:
    tags.update(block_class.tags)

tag_dict = {tag: [block_class for block_class in block_classes
                  if tag in block_class.tags] for tag in tags}
