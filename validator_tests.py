# -*- coding: utf-8 -*-

from validator import *


def no_nest_Any_test():
    v = Any(Int(), String())
    assert v('12345')
    assert v(3345)
    assert v('aaa')

def no_nest_All_test():
    v = All(AllowType(int), String())
    assert v('2355')
    assert not v(2355)
    assert not v('abcd')



def number_test():
    v = Number()
    assert v(1)
    assert v(442300)
    assert v('3445')
    assert v(1.33)
    assert v('3.1415')
    assert not v('ab')

    vmin = Number(min=0)
    assert vmin(0)
    assert vmin(1)
    assert not vmin(-1)
    assert not vmin(-0.01)
    assert vmin('0')
    assert vmin(65536)
    assert not vmin('hogepiyo')

    vmax = Number(max=10)
    assert vmax(10)
    assert vmax(9)
    assert not vmax(11)
    assert not vmax(10.01)
    assert vmax('10')
    assert vmax(-2000)
    assert not vmax('x23456')

    vmm = Number(min=0, max=100)
    assert vmm(0)
    assert vmm(100)
    assert not vmm(-1)
    assert not vmm(101)
    assert vmm(30)

def freetext_test():
    v = FreeText()
    assert v('hoge')
    assert v('232122')
    assert v('a33453')
    assert v('寿限無寿限無五劫の擦り切れ')
    assert v(u'寿限無寿限無五劫の擦り切れ')
    assert v('寿限無寿限無五劫の擦り切れ\n海砂利水魚の')
    assert v(u'寿限無寿限無五劫の擦り切れ\n海砂利水魚の')
    assert not v(frozenset([1,2,3]))

    vban = FreeText(ban_phrases=['ho', u'五劫'])
    assert vban('moge')
    assert vban('寿限無')
    assert vban(u'の擦り切れ')
    assert not vban('hoge')
    assert vban('寿限無寿限無五劫の擦り切れ')
    assert not vban(u'寿限無寿限無五劫の擦り切れ')
    assert not vban('五劫のho')
    assert not vban(u'五劫のho')

    vig = FreeText(ignore_chars=['oge', '擦り切れ'])
    assert vig('moge')
    assert vig('寿限無寿限無五劫の擦り切れ')
    assert vig(u'寿限無寿限無五劫の擦り切れ')

    vbi = FreeText(ban_phrases=['oge', '擦り切'], ignore_chars=['hoge', '五劫の擦り切れ'])
    assert vbi('hogetaxi')
    assert not vbi('xoge')
    assert vbi('寿限無寿限無五劫の擦り切れ')
    assert vbi(u'寿限無寿限無五劫の擦り切れ')
    assert not vbi('の擦り切れ')
    assert not vbi('五●の擦り切れ')


def equal_test():
    v = Equal('1')
    assert v('1')
    assert v(u'1')
    assert not v(1)

    v2 = Equal(u'寿限無')
    assert v2(u'寿限無')
    assert v2('寿限無')


def regex_test():
    verr = Regex(1)
    assert not verr('abc')

    vm = Regex('^hoge')
    assert vm('hoge')
    assert not vm('xhoge')
    assert vm('hogep')

    vs = Regex('ho.+ge', is_match=False)
    assert vs('hoxge')
    assert vs('hoxgep')
    assert vs('dhoahfoejaiohoxgep')
    assert not vs('hoge')

    vmf = Regex('ho.ge', flags='imlsux')
    assert not vmf('hoge')
    assert vmf('HooGe')

    vsf = Regex('hopi', flags=set('lmsuix'))
    assert vsf('hopi')


def allowtype_test():
    v = AllowType(int)
    assert v(1)
    assert v('4423')
    assert not v('jugem')

    def func(exc):
        try:
            raise exc
        except ValueError:
            return True
        return False
    vex = AllowType(float, on_exception=func)
    assert vex('aaa')
    assert vex(1.23)


def prefix_test():
    v_ab = Prefix('abc')
    assert v_ab('abcdef')
    assert v_ab('abc221')
    assert not v_ab('axc000')
    v_num = Prefix(23)
    assert v_num(2344)
    assert v_num('2345')
    assert not v_num(2244)


def type_test():
    vint = Type(int)
    assert vint(100)
    assert not vint('100')

    vbs = Type(basestring)
    assert vbs('aaa')
    assert vbs(u'君は誰とホトトギス')
    assert not vbs(1)


def length_test():
    v = Length()
    assert v('1234567890')
    assert v('X' * 1000)

    vmin = Length(min=5)
    assert vmin('12345')
    assert not vmin('1234')
    assert not vmin('')

    vmax = Length(max=10)
    assert vmax('1234567890')
    assert vmax('')
    assert not vmax('1234567890a')


def onelinertext_test():
    v = OnelinerText()
    assert v('abcdefg')
    assert v('abcdefg' * 100)
    assert not v('abcdef\nGHIJ')
    assert not v('寿限無\n寿限無')
    assert not v(u'寿限無\n寿限無\n')
    assert not v('''寿限無
    寿限無''')
    assert not v(u'''寿限無
    寿限無''')


def string_test():
    v = String()
    assert v('abcdef')
    assert v('12345')
    assert not v(1)


def int_test():
    v = Int()
    assert v(111)
    assert not v('1234')
    assert not v('abcdef')


def sortorder_test():
    v = SortOrder()
    assert v('asc')
    assert v('desc')
    assert not v('ascd')
    assert not v('description')


def flag_test():
    v = Flag()
    assert v('true')
    assert v('t')
    assert v('1')
    assert v('false')
    assert v('f')
    assert v('0')



if __name__ == '__main__':
    import nose
    nose.main()

