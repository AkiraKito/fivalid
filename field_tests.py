# -*- coding: utf-8 -*-


from fields import *
from validators import *
from converters import *



def basefield_test():
    f = BaseField(validators=All(Number(min=3), Length(max=10)))
    value = f('7')
    assert isinstance(value, unicode)
    assert value == u'7'

    f = BaseField(default=12334, validators=Any(Equal('x'), Int()))
    value = f(1)
    assert isinstance(value, unicode)
    assert value == u'1'
    value = f(None)
    assert value == u'12334'

    f3 = BaseField(validators=Equal('m'), empty_value='')
    value = f3('')
    assert value is None
    try:
        f3('x')
    except ValidationError:
        pass
    else:
        raise AssertionError

    freq = BaseField(required=True, validators=Equal('zx'))
    try:
        freq(None)
    except RequiredError:
        pass
    else:
        raise AssertionError

    rconv = BaseField(validators=Equal('mmm'))
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


