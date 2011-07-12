# -*- coding: utf-8 -*-

from ..converters import (
    ConversionError,
    unicode_converter,
    float_converter,
    int_converter,
    truthvalue_converter,
    colon_separated_converter
)


def unicode_converter_test():
    value = unicode_converter(None, 'abcdef')
    assert isinstance(value, unicode)
    value = unicode_converter(None, u'abcdefg')
    assert isinstance(value, unicode)
    value = unicode_converter(None, '寿限無寿限無五劫の擦り切れ')
    assert isinstance(value, unicode)
    value = unicode_converter(None, u'寿限無寿限無五劫の擦り切れ')
    assert isinstance(value, unicode)


def float_converter_test():
    value = float_converter(None, '123')
    assert isinstance(value, float)
    value = float_converter(None, 123)
    assert isinstance(value, float)
    value = float_converter(None, 123.5)
    assert isinstance(value, float)
    try:
        float_converter(None, 'a')
    except ConversionError:
        pass
    else:
        raise AssertionError


def int_converter_test():
    value = int_converter(None, '123')
    assert isinstance(value, int)
    value = int_converter(None, 123)
    assert isinstance(value, int)
    value = int_converter(None, 123.5)
    assert isinstance(value, int)
    try:
        int_converter(None, 'a')
    except ConversionError:
        pass
    else:
        raise AssertionError


def truthvalue_converter_test():
    value = truthvalue_converter(None, 'True')
    assert isinstance(value, bool)
    assert value == True
    value = truthvalue_converter(None, 'true')
    assert isinstance(value, bool)
    assert value == True
    value = truthvalue_converter(None, 't')
    assert isinstance(value, bool)
    assert value == True
    value = truthvalue_converter(None, '1')
    assert isinstance(value, bool)
    assert value == True
    
    value = truthvalue_converter(None, 'False')
    assert isinstance(value, bool)
    assert value == False
    value = truthvalue_converter(None, 'false')
    assert isinstance(value, bool)
    assert value == False
    value = truthvalue_converter(None, 'f')
    assert isinstance(value, bool)
    assert value == False
    value = truthvalue_converter(None, '0')
    assert isinstance(value, bool)
    assert value == False

    try:
        truthvalue_converter(None, 'balse')
    except ConversionError:
        pass
    else:
        raise AssertionError


def colon_separated_converter_test():
    value = colon_separated_converter(None, 'x:y')
    assert isinstance(value, tuple)
    assert value[0] == 'x'
    assert value[1] == 'y'
    
    try:
        colon_separated_converter(None, u'ああああ')
    except ConversionError:
        pass
    else:
        raise AssertionError



if __name__ == '__main__':
    import nose
    nose.main()

