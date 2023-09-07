*********
Changelog
*********

This project follows the guidelines of `Keep a changelog`_ and adheres to
`Semantic versioning`_.

.. _Keep a changelog: http://keepachangelog.com/
.. _Semantic versioning: https://semver.org/

0.4.2 - 2023-07-9
=================

Added
-----
* MacOS CI workflow

Changed
-------
* Normalize input data for audio player

Fixed
-----
* Fixed a bug using wayland not loading pyside6 modules

0.4.1 - 2023-05-9
=================

Added
-----
* Downsample block

Changed
-------
* Audio Player now detects the sampling frequency

Removed
-------
* Temporarily removed introduction window

Fixed
-----
* Fixed some issues with the file parameters


0.4.0 - 2023-31-8
=================

Added
-----
* Embedded matplotlib plots
* Normalize block
* Impulse block
* Convolution block
* FFT Shift block
* Plot options
* Added `icons <https://www.freepik.com>`_ to toolbar
* Framework for parameter descriptions
* Option to add code references to a block
* Add opening files from command line

Changed
-------
* Double clicking a block sets it to a random position
* Tags are switched with a check box instead of a combo box
* Add decorators in the util module to make validation easier
* Replace .json file by using dsch to save and load signals
* Update from PySide2 to PySide6
* GUI implicitly localizes strings
* Block names
* Block descriptions
* Audio blocks now allow 2 channels


Fixed
-----
* Deleting blocks did not free them from memory resulting in a memory leak
* Only open context menu when blocks are clicked

0.3.0 - 2022-01-06
==================

Added
-----
* Context menu for editing actions
* High DPI scaling
* Logging
* The block explorer can now be realigned
* Histogramm plot block
* Connection lines can now be removed by right-clicking



Changed
-------
* SignalPlot has been renamed to Plot

    * Implements also a bar and stem plot
* Renamed the FFT tag
* Reworked how the connection lines are implemented
* Editing windows are blocking now

Fixed
-----
* Set environment variable to select the PySide2 installation when using Anaconda
* The plot view sometimes would not update its default view

0.2.0 - 2022-17-02
==================

Added
-----
* Dark mode
* Item selection
* Editing features (copy, paste, cut)
* Background pattern

Changed
-------
* Rework the Blocklist
* Change the colour styles of some graphic items

Fixed
-----
* Include the version file to the package data



0.1.0 - 2021-12-09
==================

Added
-----
* Initial implementation.
