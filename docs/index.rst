.. field validator documentation master file, created by
   sphinx-quickstart on Wed Jul 13 01:37:53 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fivalid's documentation!
===========================================


About
-----
.. automodule:: __init__


Contents:
---------

.. toctree::
    :maxdepth: 2
    
    fields.rst
    validators.rst
    converters.rst
    structures.rst


Exceptions
----------
.. autoexception:: fields.RequiredError

.. autoexception:: validators.ValidationError

.. autoexception:: validators.InvalidValueError
    
    Subclass of :exc:`validators.ValidationError`

.. autoexception:: validators.InvalidTypeError
    
    Subclass of :exc:`validators.ValidationError`

.. autoexception:: converters.ConversionError



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



