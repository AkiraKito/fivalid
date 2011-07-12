.. field validator documentation master file, created by
   sphinx-quickstart on Wed Jul 13 01:37:53 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to field validator's documentation!
===========================================


fields
------
.. autoclass:: fields.BaseField
    :members: __call__


validators
----------
.. autoclass:: validators.All

.. autoclass:: validators.Any

.. autoclass:: validators.Validator

.. autoclass:: validators.Number

.. autoclass:: validators.FreeText

.. autoclass:: validators.Equal

.. autoclass:: validators.Regex

.. autoclass:: validators.AllowType

.. autoclass:: validators.Prefix

.. autoclass:: validators.Type

.. autoclass:: validators.Length

.. autoclass:: validators.OnelinerText

.. autoclass:: validators.String

.. autoclass:: validators.Int

.. autoclass:: validators.SortOrder

.. autoclass:: validators.Flag


converters
----------
.. autofunction:: converters.unicode_converter

.. autofunction:: converters.float_converter

.. autofunction:: converters.int_converter

.. autofunction:: converters.truthvalue_converter

.. autofunction:: converters.colon_separated_converter


exceptions
----------
.. autoexception:: fields.RequiredError

.. autoexception:: validators.ValidationError

.. autoexception:: converters.ConversionError



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



