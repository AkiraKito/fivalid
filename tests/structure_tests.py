# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import nottest

from ..fields import BaseField, RequiredError
from ..validators import (
    Type, Equal, Number, String,
    Any, All, Failure, ValueAdapter,
    ValidationError
)
from ..converters import int_converter
from .. structures import Seq, Dict, StructuredFields



from itertools import cycle

class SequenceRuleTest(TestCase):

    def test_init(self):
        rule = Seq(Equal('X'), type=list)
        
        assert hasattr(rule, 'data_validator')
        assert isinstance(rule.data_validator, Type)
        assert rule.data_validator([]) == None
        self.assertRaises(ValidationError, rule.data_validator, {})
        
        assert hasattr(rule, 'rules')
        assert isinstance(rule.rules, list)

        assert hasattr(rule, '__len__')
        assert len(rule) == 1
    
    def test_pattern_repeat(self):
        rule = Seq(
            Equal('A'),
            Any(Equal('A'), Equal('B')),
            Any(Equal('B'), Equal('C'))
        )
        r = rule.get(0)
        assert isinstance(r, Equal)
        assert r('A') == None
        self.assertRaises(ValidationError, r, 'B')
        self.assertRaises(ValidationError, r, 'C')
        
        r = rule.get(1)
        assert isinstance(r, Any)
        assert r('A') == None
        assert r('B') == None
        self.assertRaises(ValidationError, r, 'C')
        
        r = rule.get(2)
        assert isinstance(r, Any)
        assert r('B') == None
        assert r('C') == None
        self.assertRaises(ValidationError, r, 'A')

    def test_rule_accessor_get(self):
        rule = Seq(Equal('X'), Equal('Y'))
        assert rule[0] == Equal('X')
        assert rule[1] == Equal('Y')
        assert rule[2] == Equal('X')
        assert rule[3] == Equal('Y')
        assert rule[5] == Equal('Y')

    def test_rule_accessor_iter(self):
        rule = Seq(Equal('X'), Equal('Y'))
        _rule = [Equal('X'), Equal('Y')]
        for i, r in enumerate(rule):
            assert r == _rule[i]

    def test_rule_accessor_set(self):
        rule = Seq(Equal('xxx'), Equal('Y'))
        
        rule[0] = String()
        assert rule[0] == String()
        assert rule[1] == Equal('Y')
        try:
            rule[2] = String()
        except IndexError:
            pass
        else:
            raise AssertionError()
        
        length = len(rule)
        rule.insert(Equal('aaa'))
        assert len(rule) == length + 1
        assert rule[len(rule)-1] == Equal('aaa')
        
        length = len(rule)
        rule.insert(Equal('bbb'), 0)
        assert len(rule) == length + 1
        assert rule[0] == Equal('bbb')
        rule.insert(String(), len(rule) + 100)
        assert rule[len(rule)-1] == String()
    
    def test_rule_accessor_delete(self):
        rule = Seq(String(), Equal('aaa'))
        del rule[0]
        assert len(rule) == 1
        assert rule[0] == Equal('aaa')


class DictRuleTest(TestCase):
    
    def setUp(self):
        self.rule = Dict({'a': Equal('Abort')}, b=Equal('Break'))

    def test_init(self):
        rule = self.rule
        
        assert hasattr(rule, 'data_validator')
        assert isinstance(rule.data_validator, All)
        assert rule.data_validator({}) == None
        self.assertRaises(ValidationError, rule.data_validator, [])
        
        assert hasattr(rule, 'rules')
        assert isinstance(rule.rules, dict)
        
        assert hasattr(rule, '__len__')
        assert len(rule) == 2

        rule = Dict(a=Equal('x'), __is_ignore_extra=True)
        assert hasattr(rule, 'data_validator')
        assert isinstance(rule.data_validator, Type)
        assert rule.data_validator({'a':'x'}) == None
        assert rule.data_validator({'a':'x', 'b':'y'}) == None
        self.assertRaises(ValidationError, rule.data_validator, [])
    
    def test_get_rule(self):
        rule = self.rule.get('a')
        assert isinstance(rule, Equal)
        assert rule('Abort') == None
        self.assertRaises(ValidationError, rule, 'Ubort')

        rule = self.rule.get('b')
        assert isinstance(rule, Equal)
        assert rule('Break') == None
        self.assertRaises(ValidationError, rule, 'Brake')

        assert type(self.rule.get()) == type(self.rule.get(None))
        rule = self.rule.get()
        assert isinstance(rule, Failure)

    def test_rule_accessor_get(self):
        rule = Dict(a=Equal('x'), b=Equal('y'))
        assert rule['a'] == Equal('x')
        assert rule['b'] == Equal('y')
        def x():
            return rule['c']
        self.assertRaises(KeyError, x)

    def test_rule_accessor_iter(self):
        rule = Dict(a=Equal('x'), b=Equal('y'))
        r = rule.__iter__()
        assert r.next() == Equal('x')
        assert r.next() == Equal('y')

    def test_rule_accessor_set(self):
        rule = Dict(a=Equal('x'), b=Equal('y'))
        rule['a'] = Number()
        assert rule['a'] == Number()
        assert rule['b'] == Equal('y')
        
        rule['c'] = Equal('ccc')
        assert rule['c'] == Equal('ccc')

        length = len(rule)
        rule.insert(Equal('aaa'), 'a')
        assert len(rule) == length
        assert rule['a'] == Equal('aaa')

        length = len(rule)
        rule.insert(Equal('zzz'), 'z')
        assert len(rule) == length + 1
        assert rule['z'] == Equal('zzz')

    def test_rule_accessor_delete(self):
        rule = Dict(a=String(), b=Equal('aaa'))
        del rule['a']
        assert len(rule) == 1
        def x():
            return rule['a']
        self.assertRaises(KeyError, x)
        assert rule['b'] == Equal('aaa')


class StructuredFieldsTest(TestCase):

    def setUp(self):
        self.validate = StructuredFields.validate
        
        class NameField(BaseField):
            validators = String()
        self.NameField = NameField
        class PhoneNumberField(BaseField):
            validators = Number()
        self.PhoneNumberField = PhoneNumberField
    
    def test_init(self):
        stfields = StructuredFields(
            Seq(
                Equal('A'),
                Equal('B')
            ),
            empty_value=None)
        assert hasattr(stfields, 'rule')
        assert isinstance(stfields.rule, Seq)
        assert hasattr(stfields, 'empty_value')
        assert stfields.empty_value == None
    
    def test_call_with_validator(self):
        stfields = StructuredFields(
            Seq(Equal('C')))
        
        ret = stfields(['C', 'C'])
        assert isinstance(ret, list)
        assert len(ret) == 2
        assert ret[0] == None
        assert ret[1] == None
        
        self.assertRaises(ValidationError, stfields, ['C', 'B'])

    def test_call_with_field(self):
        class TokenField(BaseField):
            validators = Any(Equal('C'), Equal('c'))
            converter = lambda field, value: value.lower()
        
        stfields = StructuredFields(
            Seq(TokenField(), type=tuple)
        )
        ret = stfields(('C', 'c'))
        assert isinstance(ret, tuple)
        assert len(ret) == 2
        assert ret[0] == 'c'
        assert ret[1] == 'c'

        stfields2 = StructuredFields(
            Dict(a=TokenField(empty_value=''),
                 b=TokenField(empty_value='')),
            empty_value='')
        ret = stfields2({'a': 'C',
                         'b': ''})
        assert isinstance(ret, dict)
        assert len(ret) == 2
        assert ret['a'] == 'c'
        assert ret['b'] == None

    def test_validate_flat_dict(self):
        rule = Dict(
            a=Number(min=100, max=100),
            b=Equal('hoge')
        )
        ret = self.validate({'a':100, 'b':'hoge'},
                            rule)
        assert isinstance(ret, dict)
        assert ret['a'] == None
        assert ret['b'] == None
        
        # extra key
        self.assertRaises(ValidationError, self.validate,
                {'a':100, 'b':'hoge', 'c':4000}, rule)
        
    def test_empty_dict(self):
        rule = Dict(
            a=Number(min=0, max=3),
            b=Dict(
                hoge=Equal('piyo'),
                fuga=Equal('moge')
            )
        )
        self.assertRaises(ValidationError,
                          self.validate,
                          {'a': 2, 'b': {}},
                          rule)

    def test_empty_seq(self):
        rule = Seq(
            Number(max=5),
            Seq(
                String()
            )
        )
        self.assertRaises(ValidationError,
                          self.validate,
                          [3, []], rule)

    def test_validate_flat_seq(self):
        # flat sequence
        rule = Seq(
            Number(),
            Any(Equal('piyo'), Equal('poyo'))
        )
        ret = self.validate([100, 'piyo', 200, 'poyo'],
                            rule)
        assert isinstance(ret, list)
        for r in ret:
            assert r == None
        self.assertRaises(ValidationError, self.validate,
                [100, 'piyo', 200, 'poyo', 'poge'], rule)

    def test_validate_flat_dict_with_field(self):
        data = {'name': 'Alan Smithy',
                'phone': '00012349876'}
        rule = Dict({
            'name': self.NameField(),
            'phone': self.PhoneNumberField()
        })
        ret = self.validate(data, rule)
        assert isinstance(ret, dict)
        assert ret['name'] == 'Alan Smithy'
        assert ret['phone'] == '00012349876'

        ret = self.validate({'name': 'John Doe'}, rule)
        assert isinstance(ret, dict)
        assert ret['name'] == 'John Doe'
        assert ret['phone'] == None

    def test_validate_required_field(self):
        rule = Dict({
            'name': self.NameField(required=True),
            'phone': self.PhoneNumberField()
        })
        ret = self.validate({'name': 'John Doe',
                             'phone': '3344567989'},
                            rule)
        assert isinstance(ret, dict)
        assert ret['name'] == 'John Doe'
        assert ret['phone'] == '3344567989'

        self.assertRaises(RequiredError, self.validate,
                {'phone': '2234567'}, rule)

        self.assertRaises(RequiredError, self.validate,
                {'name': 'Hoge',
                 'phone': []},
                Dict({
                    'name': self.NameField(required=True),
                    'phone': Seq(
                        self.PhoneNumberField(required=True)
                    )
                }))


class NestedStructuredFieldTests(TestCase):
    
    def setUp(self):
        pass

    def test_twitter_like_result(self):
        data = [
            {
                'id': 123456,
                'name': 'Hoge Piyo',
                'screen_name': 'hogepiyo',
                'followers': [234, 890, 123457]
            },
            {
                'id': 123457,
                'name': 'Zoge Piyo',
                'screen_name': 'zogepiyo',
                'followers': [234, 567, 123456]
            },
            {
                'id': 123458,
                'name': 'Moge Puyo',
                'screen_name': 'mogepuyo',
                'followers': []
            }
        ]

        class IDField(BaseField):
            validators = Number()
            converter = int_converter
        class NameField(BaseField):
            validators = String()
        class ScreenNameField(NameField):
            pass
        rule = Seq(
                Dict(
                    id=IDField(required=True),
                    name=NameField(required=True),
                    screen_name=ScreenNameField(required=True),
                    followers=Seq(
                        IDField()
                    )
                ))

        ret = StructuredFields.validate(data, rule)
        assert isinstance(ret, list)
        assert len(ret) == 3
        for i, user in enumerate(ret):
            assert isinstance(user, dict)
            assert 'id' in user
            assert user['id'] == data[i]['id']
            assert 'name' in user
            assert user['name'] == data[i]['name']
            assert 'screen_name' in user
            assert user['screen_name'] == data[i]['screen_name']
            assert 'followers' in user
            assert isinstance(user['followers'], list), i
            assert user['followers'] == data[i]['followers']


