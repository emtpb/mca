*****
Usage
*****

Most users will just start the GUI by launching the installed executable.
If installed via pip, call `mca` from the command line (if you have added
your python scripts path to your PATH).

However, it is also possible to use Multi Channel Analyzer programmatically
in a project, for example::

   from mca import blocks
   # Example for plotting the absolute of the FFT of a sine signal
   sine_block = blocks.SignalGeneratorPeriodic(freq=3)
   abs_block = blocks.Absolute()
   fft_block = blocks.FFT()
   plot_block = blocks.SignalPlot()
   # Connecting the blocks
   fft_block.inputs[0].connect(sine_block.outputs[0])
   abs_block.inputs[0].connect(fft_block.outputs[0])
   plot_block.inputs[0].connect(abs_block.outputs[0])
   plot_block.show()
