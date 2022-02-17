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


How to use
==========

After installing the package, run the following command:

.. code-block:: console

    $ mca


Issues when using Anaconda
==========================

When having Anaconda installed you might get the error that some plugins
could not be loaded.

Before running the MCA set the environment variable QT_PLUGIN_PATH to the
path where the PySide2 plugins are located. It will look something like this:

.. code-block:: console

    $ export QT_PLUGIN_PATH=Your_python_installation_path/PySide2/Qt/plugins

or

.. code-block:: console

    $ export QT_PLUGIN_PATH=Your_python_installation_path/PySide2/plugins

You might want to consider putting this command into your shell config.