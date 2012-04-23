# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.join('..', 'fivalid'))
from validators import (
    ValidationError, InvalidTypeError, InvalidValueError,
    All, Any,
    ValueAdapter,
    Not,
    Failure, Pass,
    Number, FreeText, Equal, Regex,
    AllowType, Prefix, Type, Length,
    OnelinerText, String, Int,
    SortOrder, Flag, Split
)


def err(validator, value, exc=None):
    if exc is not None:
        try:
            validator(value)
        except exc:
            pass
        else:
            raise AssertionError('%s is not raised' % exc)
    else:
        try:
            validator(value)
        except ValidationError:
            pass
        else:
            raise AssertionError


def suc(validator, value):
    try:
        validator(value)
    except ValidationError, e:
        raise AssertionError(e)


def no_nest_Any_test():
    v = Any(Int(), String())
    suc(v, '12345')
    suc(v, 3345)
    suc(v, 'aaa')


def no_nest_All_test():
    v = All(AllowType(int), String())
    suc(v, '2355')
    err(v, 2355)
    err(v, 'abcd')


def value_adapter_test():
    class TestValueAdapter(ValueAdapter):
        def on_adapt(self, value):
            return str(value)
    v = TestValueAdapter(Number())
    if not isinstance(v.on_adapt(100), basestring):
        raise AssertionError
    suc(v, 100)
    suc(v, '200')
    err(v, 'a')

def not_test():
    v = Not(Equal(2))
    suc(v, '2000')
    err(v, 2)

def failure_test():
    v = Failure()
    err(v, None)
    err(v, 'none')
    err(v, 200)

def pass_test():
    v = Pass()
    suc(v, None)
    suc(v, 300)

def number_test():
    v = Number()
    suc(v, 1)
    suc(v, 442300)
    suc(v, '3445')
    suc(v, 1.33)
    suc(v, '3.1415')
    err(v, 'ab', InvalidValueError)
    err(v, dict(), InvalidTypeError)

    vmin = Number(min=0)
    suc(vmin, 0)
    suc(vmin, 1)
    err(vmin, -1, InvalidValueError)
    err(vmin, -0.01, InvalidValueError)
    suc(vmin, '0')
    suc(vmin, 65536)
    err(vmin, 'hogepiyo', InvalidValueError)

    vmax = Number(max=10)
    suc(vmax, 10)
    suc(vmax, 9)
    err(vmax, 11, InvalidValueError)
    err(vmax, 10.01, InvalidValueError)
    suc(vmax, '10')
    suc(vmax, -2000)
    err(vmax, 'x23456', InvalidValueError)

    vmm = Number(min=0, max=100)
    suc(vmm, 0)
    suc(vmm, 100)
    err(vmm, -1, InvalidValueError)
    err(vmm, 101, InvalidValueError)
    suc(vmm, 30)

def freetext_test():
    v = FreeText()
    suc(v, 'hoge')
    suc(v, '232122')
    suc(v, 'a33453')
    suc(v, '寿限無寿限無五劫の擦り切れ')
    suc(v, u'寿限無寿限無五劫の擦り切れ')
    suc(v, '寿限無寿限無五劫の擦り切れ\n海砂利水魚の')
    suc(v, u'寿限無寿限無五劫の擦り切れ\n海砂利水魚の')
    err(v, frozenset([1,2,3]), InvalidTypeError)

    vban = FreeText(ban_phrases=['ho', u'五劫'])
    suc(vban, 'moge')
    suc(vban, '寿限無')
    suc(vban, u'の擦り切れ')
    err(vban, 'hoge', InvalidValueError)
    suc(vban, '寿限無寿限無五劫の擦り切れ')
    err(vban, u'寿限無寿限無五劫の擦り切れ', InvalidValueError)
    err(vban, '五劫のho', InvalidValueError)
    err(vban, u'五劫のho', InvalidValueError)

    vig = FreeText(ignore_chars=['oge', '擦り切れ'])
    suc(vig, 'moge')
    suc(vig, '寿限無寿限無五劫の擦り切れ')
    suc(vig, u'寿限無寿限無五劫の擦り切れ')

    vbi = FreeText(ban_phrases=['oge', '擦り切'], ignore_chars=['hoge', '五劫の擦り切れ'])
    suc(vbi, 'hogetaxi')
    err(vbi, 'xoge', InvalidValueError)
    suc(vbi, '寿限無寿限無五劫の擦り切れ')
    suc(vbi, u'寿限無寿限無五劫の擦り切れ')
    err(vbi, 'の擦り切れ', InvalidValueError)
    err(vbi, '五●の擦り切れ', InvalidValueError)


def equal_test():
    v = Equal('1')
    suc(v, '1')
    suc(v, u'1')
    err(v, 1, InvalidValueError)
    err(v, '2', InvalidValueError)
    err(v, 2, InvalidValueError)

    v2 = Equal(u'寿限無')
    suc(v2, u'寿限無')
    suc(v2, u'寿限無'.encode('utf-8'))
    err(v2, u'寿限無'.encode('euc-jp'), InvalidValueError)


def regex_test():
    err(Regex, 1, TypeError)

    vterr = Regex('hoge')
    err(vterr, 100, InvalidTypeError)

    vm = Regex('^hoge')
    suc(vm, 'hoge')
    err(vm, 'xhoge', InvalidValueError)
    suc(vm, 'hogep')

    vs = Regex('ho.+ge', is_match=False)
    suc(vs, 'hoxge')
    suc(vs, 'hoxgep')
    suc(vs, 'dhoahfoejaiohoxgep')
    err(vs, 'hoge', InvalidValueError)

    vmf = Regex('ho.ge', flags='imlsux')
    err(vmf, 'hoge', InvalidValueError)
    suc(vmf, 'HooGe')

    vsf = Regex('hopi', flags=set('lmsuix'))
    suc(vsf, 'hopi')


def allowtype_test():
    err(AllowType, [], ValueError)

    v = AllowType(int)
    suc(v, 1)
    suc(v, '4423')
    err(v, 'jugem', InvalidValueError)
    err(v, {}, InvalidTypeError)

    def func(exc):
        try:
            raise exc
        except ValueError:
            pass
        else:
            raise AssertionError('ValueError is not raised')
    vex = AllowType(float, on_exception=func)
    suc(vex, 'aaa')
    suc(vex, 1.23)


def prefix_test():
    v_ab = Prefix('abc')
    suc(v_ab, 'abcdef')
    suc(v_ab, 'abc221')
    err(v_ab, 'axc000', InvalidValueError)
    
    v_num = Prefix(23)
    suc(v_num, 2344)
    suc(v_num, '2345')
    err(v_num, 2244, InvalidValueError)


def type_test():
    vint = Type(int)
    suc(vint, 100)
    err(vint, '100', InvalidTypeError)

    vbs = Type(basestring)
    suc(vbs, 'aaa')
    suc(vbs, u'君は誰とホトトギス')
    err(vbs, 1, InvalidTypeError)


def length_test():
    v = Length()
    suc(v, '1234567890')
    suc(v, 'X' * 1000)

    vmin = Length(min=5)
    suc(vmin, '12345')
    err(vmin, '1234', InvalidValueError)
    err(vmin, '', InvalidValueError)

    vmax = Length(max=10)
    suc(vmax, '1234567890')
    suc(vmax, '')
    err(vmax, '1234567890a', InvalidValueError)


def onelinertext_test():
    v = OnelinerText()
    suc(v, 'abcdefg')
    suc(v, 'abcdefg' * 100)
    err(v, 'abcdef\nGHIJ', InvalidValueError)
    err(v, '寿限無\n寿限無', InvalidValueError)
    err(v, u'寿限無\n寿限無\n', InvalidValueError)
    err(v, '''寿限無
    寿限無''', InvalidValueError)
    err(v, u'''寿限無
    寿限無''', InvalidValueError)


def string_test():
    v = String()
    suc(v, 'abcdef')
    suc(v, '12345')
    err(v, 1, InvalidTypeError)


def int_test():
    v = Int()
    suc(v, 111)
    err(v, '1234', InvalidTypeError)
    err(v, 'abcdef', InvalidTypeError)


def sortorder_test():
    v = SortOrder()
    suc(v, 'asc')
    suc(v, 'desc')
    err(v, 'ascd', InvalidValueError)
    err(v, 'description', InvalidValueError)


def flag_test():
    v = Flag()
    suc(v, 'true')
    suc(v, 't')
    suc(v, '1')
    suc(v, 'false')
    suc(v, 'f')
    suc(v, '0')
    suc(v, 'TRUE')
    suc(v, 'F')


def split_test():
    v = Split(Equal('HMX'), Number(max=16), sep='-')
    suc(v, 'HMX-1')
    suc(v, 'HMX-13')
    suc(v, 'HMX-16')
    
    err(v, 'HMX-16a', InvalidValueError)
    
    err(v, 'MMX-1', InvalidValueError)

    err(v, 'HMX@16', InvalidValueError)

    err(v, 'HMX-00-1', InvalidValueError)

    v = Split(
        Equal('HMX'),
        Any(Equal('16a'), Equal('16b'), Equal('16c')),
        sep='-')
    suc(v, 'HMX-16a')
    suc(v, 'HMX-16b')
    suc(v, 'HMX-16c')

    err(v, 'HMX-16', InvalidValueError)

    # left match
    v = Split(Pass(), Number(), sep='-')
    suc(v, 'xxxxxxx-1024')
    suc(v, '-4423')

    err(v, '---3', InvalidValueError)

    # right match
    v = Split(Pass(), Number(), Number(), sep='-', rmatch=True)
    suc(v, 'xxxxx200-300-400')
    suc(v, '-300-400')

    # can not decode to unicode
    class Moge(object):
        def __repr__(self):
            return u'もげ-200'.encode('euc-jp')
    v = Split(Pass(), Number(), sep='-')
    err(v, Moge(), InvalidValueError)


if __name__ == '__main__':
    import nose
    nose.main()

