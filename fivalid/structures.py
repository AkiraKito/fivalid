# -*- coding: utf-8 -*-

"""
    Structured data validation and conversion.
"""


import validators

class StructuredFields(object):
    """Structured Field set.
    
    *Structured* means sequence (list, tuple, dict, and more) 
    contains data.
    
    Rule (Field and Validator) should also structured.
    
    Rule is based on :class:`Dict` and :class:`Seq`. 
    :class:`Dict` is :obj:`dict`, :class:`Seq` is sequence types else.
    
    Leaf node of the rule structure have to set Field or Validator.
    
    usage:
        >>> import validators
        >>> data = {
        ...   'binary': (0,1)
        ...   'quaternary': [ 0,1,2,3 ]
        ... }
        >>> stfields = StructuredFields(
        ...   Dict(
        ...     binary=Seq(
        ...       validators.Number(min=0, max=1),
        ...       type=tuple),
        ...     quaternary=Seq(
        ...       validators.Number(min=0, max=3))
        ...   ),
        ...   empty_value=None)
        >>> stfields(data)
        {'binary': (None, None), 'quaternary': [None, None, None, None]}
        >>> from fields import BaseField
        >>> class BinaryField(BaseField):
        ...   validator = validators.Number(min=0, max=1)
        >>> class QuaternaryField(BaseField):
        ...   validator = validators.Number(min=0, max=3)
        >>> rule = Dict(
        ...   binary=Seq(
        ...     BinaryField(required=True),
        ...     type=tuple),
        ...   quaternary=Seq(
        ...     QuaternaryField()
        ... )
        >>> stfields = StructuredFields(rule)
        >>> stfields(data)
        {'binary': (u'0', u'1'), 'quaternary': [u'0', u'1', u'2', u'3']}
        >>> StructuredFields.validate(data, rule)
        {'binary': (u'0', u'1'), 'quaternary': [u'0', u'1', u'2', u'3']}
        >>> 
    """
    
    def __init__(self, rule, empty_value=None):
        self.rule = rule
        self.empty_value = empty_value

    def __call__(self, data):
        return self.validate(data, self.rule,
                empty_value=self.empty_value)
    
    @classmethod
    def validate(cls, data, rule, empty_value=None):
        """Validate data by rule.
        
        :param data: Data structure.
        :param rule: A rule set.
        :param empty_value: Validator or Field's empty case value.
                            :obj:`None` is default.
        :exception ValidationError: Error occurred while validation.
        :exception RequiredError: Field is given empty-value 
                                  despite `required` flag is :obj:`True`.
        :exception ConversionError: Error occurred in Field's converter.
                                    Conversion is failed.
        :return: Converted data has the same as input data structure.
                 If use Field, to set converted value to a part of return data.
                 But if use Validator, to set :obj:`None` to one.
        """
        if hasattr(data, '__iter__'):
            rule(data)  # container type validation
            if isinstance(data, dict):
                obj = dict()
                add_to_obj = obj.__setitem__
            else:
                obj = list()
                add_to_obj = lambda index, value: obj.append(value)
            # rule based scan
            for ident in rule.iteridents():
                try:
                    data_ = data[ident]
                except KeyError:
                    # data is missing key, for dict
                    data_ = empty_value
                except IndexError:
                    # end of data, for other sequence
                    if len(data) == 0:
                        # empty container
                        cls.validate(empty_value, rule.get(ident),
                                    empty_value=empty_value)
                    break
                add_to_obj(ident,
                           cls.validate(data_, rule.get(ident),
                                empty_value=empty_value))
            return data.__class__(obj)
        else:
            return rule(data)


class StructureRule(object):
    """Abstruct data structure validation rule set."""
    
    def __init__(self, *rules, **options):
        self.rules = rules
        self.data_validator = validators.Type(options.pop('type', None))

    def __call__(self, value):
        """Compatible interface for Field and Validator."""
        self.data_validator(value)

    def __len__(self):
        return len(self.rules)

    def __iter__(self):
        """Iterator of all rules."""
        raise NotImplementedError

    def __getitem__(self, key):
        """Get a rule."""
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        del self.rules[key]

    def insert(self, rule, ident):
        """Insert a rule to a slot that pointed by ident.
        
        :param rule: One of rule, Validator, and Field.
        :param ident: Rule identifier.
        :exception TypeError: `ident`'s type is not acceptable.
        """
        raise NotImplementedError

    def iteridents(self):
        """Identifiers iterator of rules."""
        raise NotImplementedError

    def get(self, ident=None):
        """Rule getter."""
        raise NotImplementedError


from itertools import cycle, count

class Seq(StructureRule):
    """Sequence of rules.
    
    Get a rule in the order they were given at one time, and endless repeat the pattern.:
        >>> rule = Seq(Number(), String())
        >>> for i in range(4):
        ...   type(rule[i])
        ... 
        <class 'fivalid.validators.Number'>
        <class 'fivalid.validators.String'>
        <class 'fivalid.validators.Number'>
        <class 'fivalid.validators.String'>
        >>> 
    
    `*rules`
        :class:`Seq`, :class:`Dict`, 
        Validators, and Fields.
    `**options`
        `type`
            A type of sequence object. 
            Default is :obj:`list`.
    """

    def __init__(self, *rules, **options):
        super(Seq, self).__init__(type=options.pop('type', list),
                                  *rules)
        self.rules = list(self.rules)

    def __iter__(self):
        """Iterator of rule objects."""
        return self.rules.__iter__()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__class__(type=self.data_validator.value_type,
                                  *self.rules[key])
        try:
            return self.get(key)
        except ValueError, e:
            raise IndexError(e)

    def __setitem__(self, key, value):
        """Rule setter.
        
        Update rule from value that identified by key.
        """
        self.rules[key] = value

    def insert(self, rule, ident=None):
        """Insert a rule into rule set.
        
        usage:
            >>> rule = Seq(Equal('x'))
            >>> rule.insert(Equal('y'))
            >>> assert rule[1] == Equal('y')
            >>> rule.insert(Equal('z'), 0)
            >>> assert rule[0] == Equal('z')
            >>> 
        """
        if ident is None:
            self.rules.append(rule)
        else:
            self.rules.insert(ident, rule)

    def iteridents(self):
        """Identifiers iterator of rules.
        
        Take care that iterator continues infinitely.
        A recommended usage is to use this method with :func:`len()`.
        """
        return count(0)
    
    def get(self, ident):
        """Pattern repeat rule getter.
        
        usage:
            >>> rule = Seq(Equal('a'), Equal('b'))
            >>> assert rule.get(0) == Equal('a')
            >>> assert rule.get(1) == Equal('b')
            >>> assert rule.get(2) == Equal('a')
            >>> assert rule.get(3) == Equal('b')
            >>> assert rule.get(5) == Equal('b')
        
        :param ident: Identifier of rule that accepts integer.
        :return: A rule.
        :rtype: If leaf node of data, return Validator or Field object.
                Otherwise, return :class:`Seq` or :class:`Dict`.
        """
        try:
            ident = int(ident)
        except ValueError:
            raise
        return self.rules[ident % len(self.rules)]


class ExtraDataRejection(validators.Validator):
    def validate(self, value):
        data, rules = value
        extra_data = set(data.keys()) - set(rules)
        if extra_data:
            raise validators.ValidationError(
                'Found extra data: %s' % extra_data)

class PackAdapter(validators.ValueAdapter):
    def __init__(self, rules, *validators):
        super(PackAdapter, self).__init__(*validators)
        self.rules = rules
    
    def on_adapt(self, value):
        return (value, self.rules)

class Dict(StructureRule):
    """Dictionary of rules.
    
    `*rules`
        Dict of rules.
        
        Rules are :class:`Seq`, :class:`Dict`, 
        Validators, and Fields.
    `**kwrules`
        Rules by keyword argument.
        
        Argument value is same as `*rules`.
    `__is_ignore_extra=False`
        If this option is True, to ignore extra data 
        when find unexpected key in validatee structured data.
    """
    
    def __init__(self, *rules, **kwrules):
        is_ignore_extra = kwrules.pop('__is_ignore_extra', False)
        rules = dict(*rules, **kwrules)
        super(Dict, self).__init__(rules, type=dict)
        self.rules = self.rules[0]  # unpack tuple
        if not is_ignore_extra:
            self.data_validator = \
                validators.All(self.data_validator,
                    PackAdapter(self.rules.keys(),
                                ExtraDataRejection()))
    
    def __iter__(self):
        """Iterator of rule objects."""
        return self.rules.itervalues()

    def __getitem__(self, key):
        """Rule getter that return a rule if key is exists.
        
        :param key: Rule identifier.
        :return: A rule.
        :rtype: Same as :meth:`Dict.get`.
        """
        if key not in self.rules:
            raise KeyError(key)
        return self.get(key)

    def __setitem__(self, key, value):
        self.rules[key] = value

    def insert(self, rule, ident):
        """Update and add rule."""
        self[ident] = rule
    
    def iteridents(self):
        return self.rules.iterkeys()

    def get(self, ident=None):
        """Rule getter.
        
        If rule dict is not have key `ident`, will error occur in validation.
        
        :param ident: Key of rule dictionary.
        :return: A rule.
        :rtype: If rule is leaf node of data, return Validator or Field object.
                Otherwise, return :class:`Seq` or :class:`Dict`.
        """
        return self.rules.get(ident, validators.Failure())


