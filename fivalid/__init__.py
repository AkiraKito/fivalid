# -*- coding: utf-8 -*-

"""
    fivalid v0.1.2
    
    fivalid is lightweight field data validator.
    
    validation:
        >>> from fivalid import validators
        >>> num = validators.Number(max=20)
        >>> num(10)
        >>> num(21)
        validators.ValidationError: over max
        >>> strnum = validators.All(
        ...   validators.Number(), validators.String())
        >>> strnum('100')
        >>> strnum(100)
        validators.ValidationError: not same type
    
    field value validation and conversion:
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
        fivalid.validators.ValidationError: over max
        >>> input_data = {'lightness': '70'}
        >>> lightness_field = PercentageField(empty_value='')
        >>> lightness = lightness_field(input_data.get('lightness', ''))
        >>> print lightness
        70
        >>> input_data2 = {}
        >>> lightness = lightness_field(input_data2.get('lightness', ''))
        >>> print lightness
        None
    
    data structure validation (same data structure will be return, but *all values* are :obj:`None`. because it's **validation only** use):
        >>> from fivalid import StructuredFields, Seq, Dict
        >>> from fivalid.validators import String, Length, All, Flag
        >>> rule = Dict(
        ...   {'comment': All(String(), Length(max=500)),
        ...    'nickname': All(String(), Length(max=20)),
        ...    'remember me': Flag()}
        ... )
        >>> data = {'comment': 'Hello, fivalid.',
        ...         'nickname': 'John Doe',
        ...         'remember me': '1'}
        >>> stfields = StructuredFields(rule)
        >>> stfields(data)
        {'comment': None, 'nickname': None, 'remember me': None}
        >>> StructuredFields.validate(data, rule) # same as
        {'comment': None, 'nickname': None, 'remember me': None}
    
    data structure validation and conversion:
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
        
"""

__version__ = '0.1.1'


from validators import (
    All, Any, ValueAdapter,
    Validator,
    Number, FreeText, Equal, Regex, AllowType, Prefix, Type, Length,
    OnelinerText, String, Int, SortOrder, Flag
)

from converters import (
    unicode_converter,
    float_converter,
    int_converter,
    truthvalue_converter,
    colon_separated_converter
)

from fields import (
    ValidationError, ConversionError, RequiredError,
    BaseField
)

from structures import (
    StructuredFields,
    Seq, Dict
)

