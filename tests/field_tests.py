# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.join('..', 'fivalid'))

from fields import (
    RequiredError,
    BaseField
)
from validators import (
    ValidationError,
    All, Any,
    Number, FreeText, Equal, Regex,
    AllowType, Prefix, Type, Length,
    OnelinerText, String, Int,
    SortOrder, Flag
)
from converters import (
    ConversionError,
    unicode_converter,
    float_converter,
    int_converter,
    truthvalue_converter,
    colon_separated_converter
)



def validation_and_conversion_test():
    f = BaseField(validator=All(Number(min=3), Length(max=10)))
    value = f('7')
    assert isinstance(value, unicode)
    assert value == u'7'

def default_test():
    f = BaseField(default=12334, validator=Any(Equal('x'), Int()))
    value = f(1)
    assert isinstance(value, unicode)
    assert value == u'1'
    value = f(None)
    assert value == u'12334'

def empty_value_test():
    f = BaseField(validator=Equal('m'), empty_value='')
    value = f('')
    assert value is None
    try:
        f('x')
    except ValidationError:
        pass
    else:
        raise AssertionError

def required_test():
    freq = BaseField(required=True, validator=Equal('zx'))
    try:
        freq(None)
    except RequiredError:
        pass
    else:
        raise AssertionError

def replace_converter_test():
    rconv = BaseField(validator=Equal('mmm'))
    from functools import partial
    rconv.converter = partial(int_converter, rconv) # DO NOT normally use!
    try:
        rconv('mmm')
    except ConversionError:
        pass
    else:
        raise AssertionError



if __name__ == '__main__':
    import nose
    nose.main()


