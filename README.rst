fivalid
=======

fivalid is lightweight field data validator.

Features
--------
* data validation
    >>> from fivalid import validators
    >>> num = validators.Number(max=20)
    >>> num(10)
    >>> num(21)
    validators.InvalidValueError: over max

* data validation and conversion
    >>> from fivalid import BaseField, validators, converters
    >>> class PercentageField(BaseField):
    ...   validator = validators.All(
    ...     validators.Number(min=0, max=100),
    ...     validators.String())
    ...   converter = converters.int_converter
    >>> field = PercentageField()
    >>> field('99')
    99
    >>> field('200')
    fivalid.validators.InvalidValueError: over max

* structured data (e.g. nested dict, nested list) validation and conversion
    >>> from fivalid import StructuredFields, Seq, Dict, BaseField
    >>> from fivalid.validators import String, Length, All, Flag
    >>> from fivalid.converters import truthvalue_converter
    >>> class CommentField(BaseField): validator = All(String(), Length(max=500))
    >>> class NicknameField(BaseField): validator = All(String(), Length(max=20))
    >>> class RememberMeField(BaseField): validator = Flag(); converter = truthvalue_converter
    >>> rule = Dict(
    ...   {'comment': CommentField(required=True),
    ...    'nickname': NicknameField(),
    ...    'remember me': RememberMeField()}
    ... )
    >>> stfields = StructuredFields(rule)
    >>> stfields({'comment': 'Hello, fivalid.',
    ...           'nickname': 'John Doe',
    ...           'remember me': '1'})
    {'comment': u'Hello, fivalid.', 'nickname': u'John Doe', 'remember me': True}

