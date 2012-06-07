
Validators
==========
.. autoclass:: validators.Validator
    :members: __call__, __eq__, __ne__, validate
    :undoc-members:

    .. attribute:: ident
        
        Validator's identifier getter method (decoreted by :func:`property`).
        
        It is string that generated from Validator's all arguments.
        
        It is used by :meth:`~validators.Validator.__eq__` and :meth:`~validators.Validator.__ne__`.

.. autoclass:: validators.All

.. autoclass:: validators.Any

.. autoclass:: validators.ValueAdapter
    :members: on_adapt

.. autoclass:: validators.Not

.. autoclass:: validators.Failure

.. autoclass:: validators.Pass

.. autoclass:: validators.Number
    :members:

.. autoclass:: validators.FreeText

.. autoclass:: validators.Equal

.. autoclass:: validators.Regex
    :members: __init__

.. autoclass:: validators.AllowType
    :members: __init__

.. autoclass:: validators.Prefix

.. autoclass:: validators.Type

.. autoclass:: validators.Length

.. autoclass:: validators.Split

.. autoclass:: validators.OnelinerText

.. autoclass:: validators.String

.. autoclass:: validators.Int

.. autoclass:: validators.SortOrder

.. autoclass:: validators.Flag


