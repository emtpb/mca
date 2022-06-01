**********************
Multi Channel Analyzer
**********************

Graph based signal processing tool. Data is being passed between
blocks via inputs and outputs in a block diagram.
Allows sequential and parallel execution of various processing steps in a
easy and trivial manner.



Features
========

* Loading and saving block diagrams
* Graphical User Interface (PySide2)

    * Language Support
* Audio Support
* Support for Handyscope oscilloscope devices (HS3, HS5)

    * Using the Handyscope blocks requires manual installation of the tiepie
      library


Requirements
============

Python3.7 or greater

Under Linux you might to need to install the PortAudio
library which can be done via package manager:

.. code-block:: console

    $ sudo apt-get install libportaudio2

How to use
==========

After installing the package, you can run the following command to start the mca
(if you have added your python scripts path to your PATH):

.. code-block:: console

    $ mca