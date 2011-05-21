# -*- coding: utf-8 -*-


from fields import *
from validators import *



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



if __name__ == '__main__':
    import nose
    nose.main()


