*********************
Create your own block
*********************

.. _Overview:

Overview
========

What is a block?
----------------

A block is basically a processing unit with inputs, outputs and parameters.
Different blocks can be connected via IO and transmit/receive data. Blocks can
also have other functions apart from processing for
example plotting or recording audio.

Data types
----------

There currently exists only one data type. This data type is called
:class:`.Signal` . There are more data types planned for the future and this
needs be taken into account and is discussed in :ref:`Validation`.

The :class:`.Signal` consists of two 1-D Numpy Arrays and meta data. The two
Numpy Arrays correspond to the abscissa and the ordinate. To save storage
the abscissa is internally stored as 3 parameters instead of an entire
Numpy Array. Those parameters are: Abscissa Start, Increment and Values.

Structure of the package
------------------------

This tree view shows the structure of mca package.

::

    mca
    ├── __init__.py
    ├── blocks
        ├── __init__.py
        ├── absolute.py
        ├── acf.py
        ├── ...
    ├── framework
        ├── __init__.py
        ├── block_base.py
        ├── ...
    ├── gui
    ├── locales
        ├── de
            ├── LC_MESSAGES
                ├── messages.mo
                └── messages.po
    ├── config.py
    ├── exceptions.py
    ├── language.py
    └── main.py

The *blocks* folder contains all integrated blocks. This is where new blocks
need to be added to.

The *framework* folder contains everything that is block related and most
classes and tools for implementing new blocks.

The *gui* folder contains the GUI implementation of the mca.

The *locales* folder contains necessary gettext files for localization.

Also worth noting are the files:

    * *exceptions.py* for mca specific exceptions and

    * *language.py* loads the localization/translation from the locales folder.


First steps
===========

This guide will mostly use the dummy code below to explain common steps
for implementing a new block::

    from mca.framework import Block, parameters, data_types, util
    from mca import exceptions
    from mca.language import _

    class Dummy(Block):
    """Adds an offset to the input signal."""
        name = _("Dummy")
        description = _("Adds an offset to the input signal.")
        tags = (_("Processing"), _("Hello World"))

        def setup_io():
            self.new_input(name="Foo")
            self.new_output()


        def setup_parameters():
            self.parameters["offset"] = parameters.FloatParameter(
                name=_("Offset"), min_=0, default=1
            )

        @util.abort_all_inputs_empty
        @util.validate_type_signal
        def process():
            # Read the input data
            input_signal = self.inputs[0].data
            # Read the parameter
            offset = self.parameters["offset"].value
            # Compute the ordinate
            ordinate = input_signal.ordinate + offset
            # Apply new signal to the output
            self.outputs[0].data = data_types.Signal(
                abscissa_start=input_signal.abscissa_start,
                values=input_signal.values,
                increment=input_signal.increment,
                ordinate=ordinate)
            # Apply metadata from the input to the output
            self.outputs[0].process_metadata = self.inputs[0].metadata

This dummy block adds an offset to an input signal and returns the new signal
at the output and just passes down the metadata.

Every new block has to inherit from the base class :class:`.Block` . There
exists also the subclass :class:`.DynamicBlock`. The difference between those two
classes is that the :class:`.DynamicBlock` allows a user to add inputs and
outputs during runtime where as the :class:`.Block` has predefined inputs and
outputs. For example the :class:`.Adder` block inherits from
:class:`.DynamicBlock` and thus allows the user to add as many inputs as
needed.

For the dummy block the default :class:`.Block` class is used::

    from mca.framework import Block

    class Dummy(Block):
        pass

Next the name and a description is added as a class variable::

    from mca.framework import Block

    class Dummy(Block):
        name="Dummy"
        description ="Adds an offset to the input signal."

Every block also has to have at least one or multiple tags. A tag can any
arbitrary string and during the runtime of the GUI all unique tags from all
blocks will get extracted and all blocks get grouped by their tags in the
list view. Current existing tags are for example: "Processing", "Generating",
"Plotting", "Fourier" or "Audio". In this example "Hello World" has been
added as a new tag::

    class Dummy(Block):
    """Adds an offset to the input signal."""
        name = "Dummy"
        description = "Adds an offset to the input signal."
        tags = ("Processing", "Hello World")

An __init__ method is usually not required for blocks. However sometimes it is
needed to assign additional attributes other than block parameters. The
:class:`.Plot` for example adds another attribute *lines* to keep
track of the lines which have been plotted.


.. _IOSetup:

IO Setup
========

Every block needs inputs or outputs to pass or receive data from other blocks. This
is done by reimplementing the method *setup_io*. Within that method
:class:`Inputs <.Input>` and :class:`Outputs <.Output>` are added via calling
:any:`new_input` and :any:`new_output`. In the dummy example one
:class:`Input <.Input>` with the name "Foo" and an :class:`Output <.Output>`
have been added::

    def setup_io():
        self.new_input(name="Foo")
        self.new_output()

The method :any:`new_output` has some additional parameters for handling
metadata. It is described more in detail in the API reference.

In addition when inheriting from :class:`.DynamicBlock` setting up dynamic
inputs and outputs should be done within *setup_io*. The attributes
*dynamic_inputs* and *dynamic_outputs* define the ranges of inputs and outputs.
By default they are set to *None* stating neither inputs or outputs are dynamic.
A range of inputs is defined by the following tuple::

    self.dynamic_inputs = (min_inputs, max_inputs)

*max_inputs* can be set to *None* to indicate that there is no limit on how
many inputs can be added.

Setting up *dynamic_outputs* can done be analog to *dynamic_inputs*.

.. _ParameterSetup:

Parameter Setup
===============

In this step parameters are defined which the user can modify after
instantiating the block. This is done within the method *setup_parameters*.

Parameters are stored in the dict *parameters*. By default the *parameters*
dict contains a parameter for the block name which is by default the class
name. How additional parameters are added can be seen by this example from the
dummy block::

    def setup_parameters():
        self.parameters["offset"] = parameters.FloatParameter(name="Offset",
                                                              min_=0, default=1)


The available parameter classes are listed in :ref:`parameters`.


Parameter blocks
----------------

The :class:`.ParameterBlock` class groups other parameters and allows
conversions if those are related to each other. This allows adding redundant
parameters without changing how the original parameters are processed or
extracted. What is meant by that is shown by the following
code extracted from the :class:`.Amplifier` block::

        factor = parameters.FloatParameter(name=_("Factor"), default=1)
        decibel = parameters.FloatParameter(name=_("Decibel"), default=0, unit="dB")

        def factor_to_decibel():
            decibel.value = 10*np.log10(factor.value)

        def decibel_to_factor():
            factor.value = 10 ** (decibel.value / 10)

        conversion_0 = parameters.ParameterConversion(
            main_parameters=[factor],
            sub_parameters=[decibel],
            conversion=factor_to_decibel
        )
        conversion_1 = parameters.ParameterConversion(
            main_parameters=[decibel],
            sub_parameters=[factor],
            conversion=decibel_to_factor)

        multiplier = parameters.ParameterBlock(name=_("Amplification"),
                                               parameters={"factor": factor, "decibel": decibel},
                                               param_conversions=[conversion_0, conversion_1],
                                               default_conversion=0)
        self.parameters["multiplier"] = multiplier

With the :class:`.Amplifier` we want to amplify the input signal by a factor
or by a factor given in decibel. The desired behaviour is that the user
manipulates one of those factors and the other one gets updated automatically.


First the parameters are defined::

    factor = parameters.FloatParameter(name=_("Factor"), default=1)
    decibel = parameters.FloatParameter(name=_("Decibel"), default=0, unit="dB")

Then the conversions between the parameters are defined within functions::

        def factor_to_decibel():
            decibel.value = 10*np.log10(factor.value)

        def decibel_to_factor():
            factor.value = 10 ** (decibel.value / 10)

Along with that :class:`ParameterConversions <.ParameterConversions>` have to
be defined::

        conversion_0 = parameters.ParameterConversion(
            main_parameters=[factor],
            sub_parameters=[decibel],
            conversion=factor_to_decibel
        )
        conversion_1 = parameters.ParameterConversion(
            main_parameters=[decibel],
            sub_parameters=[factor],
            conversion=decibel_to_factor)

This has two purposes. First when one of the *main_parameters* gets modified
all *sub_parameters* get updated by invoking the conversion function. Second
those :class:`ParameterConversions <.ParameterConversions>` define in the GUI
which parameters (widgets) are active and which are disabled. Finally
a :class:`.ParameterBlock` is created and added to the parameters of the block::

        multiplier = parameters.ParameterBlock(name=_("Amplification"),
                                               parameters={"factor": factor, "decibel": decibel},
                                               param_conversions=[conversion_0, conversion_1],
                                               default_conversion=0)
        self.parameters["multiplier"] = multiplier

Another common example for using :class:`ParameterBlocks <.ParameterBlock>` is
for parametrizing an abscissa. It is sufficient using the parameters:
*abscissa_start*, *increment*, *values*. However it is convenient having
additional parameters such as: *sampling_freq* and *measure_time*.
There are multiple equivalent combinations of parameters
for parametrizing an abscissa. Since it is common for blocks which generate signals
having parameters for defining an abscissa, there exists a
:any:`utility function <create_abscissa_parameter_block>`.

.. _Validation:

Considerations for processing
=============================

The most important method for defining the behaviour of the block is
:func:`process <mca.framework.block_base.Block.process>`. There are no
restrictions when reimplementing this method, however there are some
guidelines which should be followed.

The usual steps in the processing method are:

    * 1. Validating the input data using util decorators (or manual validation)
    * 2. Reading input data and parameters
    * 3. The actual processing
    * 4. Applying data and metadata to the outputs

These steps can partially differ/be omitted for blocks with either no inputs or
no outputs.

1. Validating the input data using util decorators
--------------------------------------------------

Before processing any data from the inputs validation should be be performed.
Most of the validation can be done via using util functions as decorators.
In the Dummy example the following utility functions are used::

        @util.abort_all_inputs_empty
        @util.validate_type_signal
        def process():
            ...

The first decorator :func:`@util.abort_all_inputs_empty <mca.framework.util.abort_all_inputs_empty>`
makes the process function abort if all inputs have no data available. It also
automatically sets the data of all outs to *None*.

The second decorator :func:`@util.validate_type_signal <mca.framework.util.validate_type_signal>`
validates the data of inputs on the :class:`.Signal` type.

Other decorators for validation are listed in :mod:`mca.framework.util`.

2. Reading input data and parameters
------------------------------------

This step is fairly trivial, but provides convenience and readability::

    @util.abort_all_inputs_empty
        @util.validate_type_signal
        def process():
            # Read the input data
            input_signal = self.inputs[0].data
            # Read the parameter
            offset = self.parameters["offset"].value

The data and parameters are assigned to short name variables.

3. The actual processing
------------------------

This up to the developer itself however here is an important tip to avoid
errors or undesired behaviour of your block: When working with data of your
inputs note that the data object (for example :class:`.Signal` object) may
be provided to other blocks. Thus refrain from assigning shallow copies
and changing their attributes. This will modify also the output data
object to which your input is connected.

Avoid doing this::

    input_signal = self.inputs[0].data
    my_ordinate = input_signal.ordinate
    my_ordinate += 5

An alternative would be::

    input_signal = self.inputs[0].data
    my_ordinate = input_signal.ordinate + 5

Or use copy/deepcopy::

    import copy

    input_signal = self.inputs[0].data
    my_ordinate = copy(input_signal.ordinate)
    my_ordinate += 5

4. Applying the data on the output
----------------------------------

At the end of every :func:`process <mca.framework.block_base.Block.process>`
method data should be applied to the outputs by setting the data attribute of
the according output::


    ordinate = input_signal.ordinate + offset
    # Apply new signal to the output
    self.outputs[0].data = data_types.Signal(
        abscissa_start=input_signal.abscissa_start,
        values=input_signal.values,
        increment=input_signal.increment,
        ordinate=ordinate)
    # Apply metadata from the input to the output
    self.outputs[0].process_metadata = self.inputs[0].metadata

In the example above a new :class:`.Signal` object is instantiated and set to
the data attribute of the desired output. The metadata from the input is just
passed onto the output since adding an offset should not change the metadata.
Some blocks require to process metadata as well. The :class:`.Multiplier` block
for example multiplies the ordinate units of the input signals.


Testing/Integration
===================

In order to test or integrate a block class it has to lie within a module in
the *blocks* package. Then import your class from your module in
the __init__.py of the *blocks* package. When starting the GUI your block
should be listed in the block list.


.. _Translations:

Translations
============

Translations within MCA are handled with `gettext <https://www.gnu.org/software/gettext/>`_ .
The `python gettext package <https://docs.python.org/3/library/gettext.html>`_
is in the python standard library included.
The tool used to create, extract, update and compile translations (locales) in
this project is called `pybabel <http://babel.pocoo.org/en/latest/cmdline.html>`_ .
In general all displayed strings such as the block name, the description,
the tags and parameter names should be translated.

