# -*- coding: utf-8 -*-

from validator import *


def err(validator, value):
    try:
        validator(value)
    except ValidationError:
        pass
    else:
        raise AssertionError


def suc(validator, value):
    try:
        validator(value)
    except ValidationError:
        raise AssertionError


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



def number_test():
    v = Number()
    suc(v, 1)
    suc(v, 442300)
    suc(v, '3445')
    suc(v, 1.33)
    suc(v, '3.1415')
    err(v, 'ab')

    vmin = Number(min=0)
    suc(vmin, 0)
    suc(vmin, 1)
    err(vmin, -1)
    err(vmin, -0.01)
    suc(vmin, '0')
    suc(vmin, 65536)
    err(vmin, 'hogepiyo')

    vmax = Number(max=10)
    suc(vmax, 10)
    suc(vmax, 9)
    err(vmax, 11)
    err(vmax, 10.01)
    suc(vmax, '10')
    suc(vmax, -2000)
    err(vmax, 'x23456')

    vmm = Number(min=0, max=100)
    suc(vmm, 0)
    suc(vmm, 100)
    err(vmm, -1)
    err(vmm, 101)
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
    err(v, frozenset([1,2,3]))

    vban = FreeText(ban_phrases=['ho', u'五劫'])
    suc(vban, 'moge')
    suc(vban, '寿限無')
    suc(vban, u'の擦り切れ')
    err(vban, 'hoge')
    suc(vban, '寿限無寿限無五劫の擦り切れ')
    err(vban, u'寿限無寿限無五劫の擦り切れ')
    err(vban, '五劫のho')
    err(vban, u'五劫のho')

    vig = FreeText(ignore_chars=['oge', '擦り切れ'])
    suc(vig, 'moge')
    suc(vig, '寿限無寿限無五劫の擦り切れ')
    suc(vig, u'寿限無寿限無五劫の擦り切れ')

    vbi = FreeText(ban_phrases=['oge', '擦り切'], ignore_chars=['hoge', '五劫の擦り切れ'])
    suc(vbi, 'hogetaxi')
    err(vbi, 'xoge')
    suc(vbi, '寿限無寿限無五劫の擦り切れ')
    suc(vbi, u'寿限無寿限無五劫の擦り切れ')
    err(vbi, 'の擦り切れ')
    err(vbi, '五●の擦り切れ')


def equal_test():
    v = Equal('1')
    suc(v, '1')
    suc(v, u'1')
    err(v, 1)

    v2 = Equal(u'寿限無')
    suc(v2, u'寿限無')
    suc(v2, '寿限無')


def regex_test():
    verr = Regex(1)
    err(verr, 'abc')

    vm = Regex('^hoge')
    suc(vm, 'hoge')
    err(vm, 'xhoge')
    suc(vm, 'hogep')

    vs = Regex('ho.+ge', is_match=False)
    suc(vs, 'hoxge')
    suc(vs, 'hoxgep')
    suc(vs, 'dhoahfoejaiohoxgep')
    err(vs, 'hoge')

    vmf = Regex('ho.ge', flags='imlsux')
    err(vmf, 'hoge')
    suc(vmf, 'HooGe')

    vsf = Regex('hopi', flags=set('lmsuix'))
    suc(vsf, 'hopi')


def allowtype_test():
    v = AllowType(int)
    suc(v, 1)
    suc(v, '4423')
    err(v, 'jugem')

    def func(exc):
        try:
            raise exc
        except ValueError:
            return True
        return False
    vex = AllowType(float, on_exception=func)
    suc(vex, 'aaa')
    suc(vex, 1.23)


def prefix_test():
    v_ab = Prefix('abc')
    suc(v_ab, 'abcdef')
    suc(v_ab, 'abc221')
    err(v_ab, 'axc000')
    v_num = Prefix(23)
    suc(v_num, 2344)
    suc(v_num, '2345')
    err(v_num, 2244)


def type_test():
    vint = Type(int)
    suc(vint, 100)
    err(vint, '100')

    vbs = Type(basestring)
    suc(vbs, 'aaa')
    suc(vbs, u'君は誰とホトトギス')
    err(vbs, 1)


def length_test():
    v = Length()
    suc(v, '1234567890')
    suc(v, 'X' * 1000)

    vmin = Length(min=5)
    suc(vmin, '12345')
    err(vmin, '1234')
    err(vmin, '')

    vmax = Length(max=10)
    suc(vmax, '1234567890')
    suc(vmax, '')
    err(vmax, '1234567890a')


def onelinertext_test():
    v = OnelinerText()
    suc(v, 'abcdefg')
    suc(v, 'abcdefg' * 100)
    err(v, 'abcdef\nGHIJ')
    err(v, '寿限無\n寿限無')
    err(v, u'寿限無\n寿限無\n')
    err(v, '''寿限無
    寿限無''')
    err(v, u'''寿限無
    寿限無''')


def string_test():
    v = String()
    suc(v, 'abcdef')
    suc(v, '12345')
    err(v, 1)


def int_test():
    v = Int()
    suc(v, 111)
    err(v, '1234')
    err(v, 'abcdef')


def sortorder_test():
    v = SortOrder()
    suc(v, 'asc')
    suc(v, 'desc')
    err(v, 'ascd')
    err(v, 'description')


def flag_test():
    v = Flag()
    suc(v, 'true')
    suc(v, 't')
    suc(v, '1')
    suc(v, 'false')
    suc(v, 'f')
    suc(v, '0')



if __name__ == '__main__':
    import nose
    nose.main()

