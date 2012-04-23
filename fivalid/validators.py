# -*- coding: utf-8 -*-

import pickle
import hashlib
import re
import itertools


class ValidationError(BaseException):
    """Error occurred while validation."""
    pass

class InvalidValueError(ValidationError):
    """Value is invalid."""
    pass

class InvalidTypeError(ValidationError):
    """Value type is invalid."""
    pass



class ValidatorBaseInterface(object):
    """Abstract validator base interface.
    
    `validators`
        Instances of some ValidatorBaseInterface's subclass.
        
        This argument is tuple.
    """
    
    def __init__(self, *validators):
        self.validators = list(validators)
        self.__hash = hashlib.sha1(
            self.__class__.__name__ +\
            pickle.dumps(self.validators, pickle.HIGHEST_PROTOCOL)).digest()

    def __call__(self, value):
        self.validate(value)

    def __eq__(self, other):
        if self.ident == other.ident:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def ident(self):
        """Identifier of instance."""
        return self.__hash

    def validate(self, value):
        """Do validate.
        
        :param value: Validatee value.
        """
        raise NotImplementedError

    def add(self, other):
        """Add new validator.
        :param other: Other validator.
        :raise TypeError: Unacceptable type was given.
        """

        if isinstance(other, ValidatorBaseInterface):
            try:
                self.validators.append(other)
            except AttributeError:
                raise
        else:
            raise TypeError('Argument is not subclass of %s.'\
                    % ValidatorBaseInterface.__class__.__name__)

    def remove(self, other):
        """Remove a validator.
        :param other: Remove target.
        """
        
        try:
            self.validators.remove(other)
        except ValueError:
            raise
        except AttributeError:
            raise


class All(ValidatorBaseInterface):
    """AND operation for validators."""

    def validate(self, value):
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError:
                raise


class Any(ValidatorBaseInterface):
    """OR operation for validators."""

    def validate(self, value):
        first_err = None
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError, e:
                if first_err is None:
                    first_err = e
            else:
                return
        if first_err is not None:
            raise first_err


class ValueAdapter(ValidatorBaseInterface):
    """Adapt value to validators when validate a value."""
    
    def on_adapt(self, value):
        """Value processor.
        
        Must be return processed value.
        """
        raise NotImplementedError
    
    def validate(self, value):
        for validator in self.validators:
            validator(self.on_adapt(value))

    def add(self, other):
        pass

    def remove(self, other):
        pass


class Validator(ValidatorBaseInterface):
    """Validator base class.
    
    Validator is identified by a combination of own *class name* and 
    *all arguments*.
    That is, validator is the same as other if one is instantiate from same class with 
    **same arguments**.
    
    inherit tips:
        call Validator.__init__() with *ALL arguments*.
    """

    def __init__(self, *args, **kwargs):
        self.__hash = hashlib.sha1(
            self.__class__.__name__ +\
            pickle.dumps(args, pickle.HIGHEST_PROTOCOL) +\
            pickle.dumps(kwargs, pickle.HIGHEST_PROTOCOL)).digest()

    @property
    def ident(self):
        return self.__hash

    def add(self, other):
        pass

    def remove(self, other):
        pass


class Not(Validator):
    """NOT operation for validator.
    
    :raises ValidationError: Not raised :exc:`ValidationError` from 
                             the validator given at initialization.
    """
    
    def __init__(self, validator):
        super(Not, self).__init__(validator)
        self.validator = validator
    
    def validate(self, value):
        try:
            self.validator(value)
        except ValidationError:
            pass
        else:
            raise ValidationError('ValidationError is not raised')


class Failure(Validator):
    """Surely fail validator.
    
    :raises ValidationError: Always the exception raises.
    """
    
    def validate(self, value):
        raise ValidationError('Surely fail')


class Pass(Validator):
    """Surely pass validator."""
    
    def validate(self, value):
        pass


class Number(Validator):
    """Number validator.

    :param min: Min of valid value.
    :param max: Max of valid value.
    """

    def __init__(self, min=None, max=None):
        super(Number, self).__init__(min, max)
        self.min = min
        self.max = max

    def validate(self, value):
        """Validate the value.

        :param value: A number.
        :type value: Accepted type of :func:`float`.
        :raise InvalidValueError: `value` is invalid.
        :raise InvalidTypeError: Type of `value` is invalid.
        """
        try:
            value = float(value)
        except ValueError, e:
            raise InvalidValueError(e)
        except TypeError, e:
            raise InvalidTypeError(e)
        if self.max is not None:
            if not (value <= self.max):
                raise InvalidValueError('over max')
        if self.min is not None:
            if not (value >= self.min):
                raise InvalidValueError('less than min')


class FreeText(Validator):
    """Free text validator.
    
    :param ban_phrases: List of ban phrase.
    :type ban_phrases: List of string.
    
    :param ignore_chars: List of ignore string. 
                         If ignore string is found in value, erase from the value 
                         when before check ban phrases.
    
    :raises InvalidTypeError: The type of given value is not string.
    :raises InvalidValueError: Ban phrase is found in the value.
    """

    def __init__(self, ban_phrases=None, ignore_chars=None):
        super(FreeText, self).__init__(ban_phrases, ignore_chars)
        self.ban_phrases = list(ban_phrases) if ban_phrases is not None else []
        self.ignore_chars = list(ignore_chars) if ignore_chars is not None else []

    def validate(self, value):
        if not isinstance(value, basestring):
            raise InvalidTypeError('not string')
        for ignore in self.ignore_chars:
            value = re.sub(ignore, '', value)
        for phrase in self.ban_phrases:
            if re.search(phrase, value) is not None:
                raise InvalidValueError('ban phrase found')


class Equal(Validator):
    """Equal value validator.
    
    :param eq_value: If the value is the same as 
                     `eq_value` is evaluated as "valid".

    .. note::
        If type of *value* is `str` and type of `eq_value` is `unicode`, 
        the *value* is treated as **UTF-8** string.

    :raises InvalidValueError: The value is not equal to `eq_value` 
                               or Failed decode `eq_value` to UTF-8.
    """

    def __init__(self, eq_value):
        super(Equal, self).__init__(eq_value)
        self.eq_value = eq_value

    def validate(self, value):
        if (not isinstance(value, basestring)) or \
                (not isinstance(self.eq_value, basestring)):
            if self.eq_value != value:
                raise InvalidValueError(
                    '%s is not equal to %s' % (value, self.eq_value))
        elif isinstance(value, unicode):
            try:
                if isinstance(self.eq_value, unicode):
                    if self.eq_value != value:
                        raise InvalidValueError(
                            '%s is not equal to %s' % (value, self.eq_value))
                elif self.eq_value.decode('utf-8') != value:
                    raise InvalidValueError(
                        '%s is not equal to %s' % (value, self.eq_value))
            except UnicodeDecodeError, e:
                raise InvalidValueError(e)
        else:
            if isinstance(self.eq_value, unicode):
                try:
                    if self.eq_value != value.decode('utf-8'):
                        raise InvalidValueError(
                            '%s is not equal to %s' % (value, self.eq_value))
                except UnicodeDecodeError, e:
                    raise InvalidValueError(e)
            elif self.eq_value != value:
                raise InvalidValueError(
                    '%s is not equal to %s' % (value, self.eq_value))


class Regex(Validator):
    """Value validation by regexp.
    
    :param regexp: Regular expression.
    :param is_match: If True, use :func:`re.match`.
                     Otherwise use :func:`re.search`.
                     
                     This flag is True by default.
    :param flags: Sequence of flags.
                  Acceptable types are: :class:`list`, :class:`tuple`, 
                  :class:`set`, :class:`frozenset`, :class:`basestring`
                  
                  * "i": :data:`re.IGNORECASE`
                  * "l": :data:`re.LOCALE`
                  * "m": :data:`re.MULTILINE`
                  * "s": :data:`re.DOTALL`
                  * "u": :data:`re.UNICODE`
                  * "x": :data:`re.VERBOSE`

    :raises InvalidValueError: Regexp pattern is not found in the value.
    """

    def __init__(self, regexp, is_match=True, flags=None):
        """Constractor.
        
        :raises TypeError: `regexp` is not string.
        """
        if isinstance(regexp, basestring):
            self.regexp = regexp
        else:
            raise TypeError('regexp is not string')
        self.is_match = is_match
        if isinstance(flags, (list, tuple, set, frozenset, basestring)):
            self.flags = 0
            if 'i' in flags: self.flags |= re.IGNORECASE
            if 'l' in flags: self.flags |= re.LOCALE
            if 'm' in flags: self.flags |= re.MULTILINE
            if 's' in flags: self.flags |= re.DOTALL
            if 'u' in flags: self.flags |= re.UNICODE
            if 'x' in flags: self.flags |= re.VERBOSE
        else:
            self.flags = None

    def validate(self, value):
        if not isinstance(value, basestring):
            raise InvalidTypeError('value is invalid')
        regex_method = re.match if self.is_match else re.search
        regex_result = regex_method(self.regexp, value)\
                if self.flags is None\
                else regex_method(self.regexp, value, self.flags)
        if regex_result is None:
            raise InvalidValueError('pattern %s is not found' % self.regexp)


class AllowType(Validator):
    """Is TYPE allowed the value?
    
    :param test_type: *Callable*. 
                      If raise exception when call this, 
                      value is evaluated as "invalid".
    
    :param on_exception: Exception callback function. 
                         When call occurred exception by `test_type`.
                         
                         Callback function takes *one* argument, 
                         it is the exception object.

    :raises InvalidTypeError: Type `test_type` can't accept the value.
    :raises InvalidValueError: Not available `on_exception` callback 
                               and exception is occurred from `test_type`.
    """

    def __init__(self, test_type, on_exception=None):
        """Constractor.
        
        :raises ValueError: `test_type` is not callable.
        """
        super(AllowType, self).__init__(test_type)
        if not callable(test_type):
            raise ValueError('`test_type` is not callable.')
        self.test_type = test_type
        self.on_exception = on_exception

    def validate(self, value):
        try:
            self.test_type(value)
        except TypeError, e:
            raise InvalidTypeError(e)
        except Exception, e:
            if callable(self.on_exception):
                self.on_exception(e)
            else:
                raise InvalidValueError(e)


class Prefix(Validator):
    """Prefix validator.
    
    :param prefix: If value that starts from `prefix`, 
                   evaluate the value as "valid".

    :raises InvalidValueError: The value is not prefixed.
    """

    def __init__(self, prefix):
        if isinstance(prefix, basestring):
            self.prefix = prefix
        else:
            self.prefix = str(prefix)
        super(Prefix, self).__init__(prefix)

    def validate(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        if not value.startswith(self.prefix):
            raise InvalidValueError(
                    'prefix %s is not found' % self.prefix)


class Type(Validator):
    """Type of the value validator.
    
    :param value_type: Expected type of the value.

    :raises InvalidTypeError: Type of the value is 
                              not same as `value_type`.
    """

    def __init__(self, value_type):
        super(Type, self).__init__(value_type)
        self.value_type = value_type

    def validate(self, value):
        if not isinstance(value, self.value_type):
            raise InvalidTypeError('not same type')


class Length(Validator):
    """Limitation of length.
    
    :param min: Min length.
    :param max: Max length.

    :raises InvalidValueError: Value has exceeded 
                               the limit of the length.
    """

    def __init__(self, min=0, max=None):
        super(Length, self).__init__(min, max)
        self.max_length = max
        self.min_length = min if min >= 0 else 0

    def validate(self, value):
        if self.max_length is not None:
            if not (len(value) <= int(self.max_length)):
                raise InvalidValueError('over max length')
        if self.min_length >= 0:
            if not (len(value) >= int(self.min_length)):
                raise InvalidValueError('less than min length')


class Split(Validator):
    """Split value validator.
    
    usage::
        
        >>> console = Any(Equal('001'), Equal('101'))
        >>> model_number = Split(Equal('HVC'), console, sep='-')
        >>> model_number('HVC-001')
        >>> model_number('HVC-002')
        validators.InvalidValueError: 002 is not equal to 001
    
    :param \*validators: Validator for splitted values.
                        
                        Number of *validators* have to same as 
                        number of part of splited values.
    :param sep: Value separator character.
                
                Value will be split by this separator string.
    :param rmatch: Right match flag.
                   
                   If this flag is :obj:`True`, 
                   to apply validator from *right side*. 
                   Otherwise, to apply validator from *left side*.
                   
                   :obj:`False` by default.
    
    :raises InvalidValueError: The value can't decode to unicode 
                               or number of splitted values and 
                               number of validators does not match.
    """
    
    def __init__(self, *validators, **options):
        sep = options.pop('sep', '-')
        rmatch = options.pop('rmatch', False)
        super(Split, self).__init__(sep=sep, rmatch=rmatch, *validators)
        self.validators = validators
        self.separator = sep
        self.rmatch = rmatch
    
    def validate(self, value):
        if not isinstance(value, basestring):
            try:
                value = unicode(value)
            except UnicodeDecodeError:
                raise InvalidValueError('Value can not decode to unicode.')
        if self.rmatch:
            splited = value.rsplit(self.separator, len(self.validators) - 1)
        else:
            splited = value.split(self.separator, len(self.validators) - 1)
        if len(splited) != len(self.validators):
            raise InvalidValueError('Number of splitted value is mismatch.')
        for validator, token in itertools.izip(self.validators, splited):
            validator(token)


# derivative

class OnelinerText(FreeText):
    """Free text without linefeed code.
    
    Arguments are the same as :class:`~validators.FreeText`.

    :raises InvalidTypeError: The type of given value is not string.
    :raises InvalidValueError: Ban phrase is found in the value.
    """

    def __init__(self, ban_phrases=None, ignore_chars=None):
        ban = [u'\n']
        if isinstance(ban_phrases, list):
            ban.extend(ban_phrases)
        super(OnelinerText, self).__init__(
                ban_phrases=ban, ignore_chars=ignore_chars)


class String(Type):
    """String type only.
    
    :raises InvalidTypeError: The type of value is not string.
    """

    def __init__(self):
        super(String, self).__init__(basestring)


class Int(Type):
    """Int type only.
    
    :raises InvalidTypeError: The type of value is not int.
    """

    def __init__(self):
        super(Int, self).__init__(int)


class SortOrder(Any):
    """Sort order validator.
    
    Acceptable value:
        ``asc``
            ascending order.
        
        ``desc``
            descending order.
    
    :raises InvalidValueError: The value is not equal to 
                               ``asc`` or ``desc``.
    """
    
    def __init__(self):
        super(SortOrder, self).__init__(Equal('asc'), Equal('desc')) 


class Flag(Any):
    """Flag validator.
    
    "true" and "t" and "1" as :obj:`True`.
    
    "false" and "f" and "0" as :obj:`False`.
    
    .. note::
        The value ignore case.
    
    :raises InvalidValueError: Not allowed value was given.
    """

    def __init__(self):
        super(Flag, self).__init__(Equal(u'true'), Equal(u't'), Equal(u'1'),
                                   Equal(u'false'), Equal(u'f'), Equal(u'0'))

    def validate(self, value):
        super(Flag, self).validate(value.lower())


