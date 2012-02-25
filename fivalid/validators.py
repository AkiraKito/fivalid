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
    """NOT operation for validator."""
    
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
    """Surely fail validator."""
    
    def validate(self, value):
        raise ValidationError('Surely fail')


class Pass(Validator):
    """Surely pass validator."""
    
    def validate(self, value):
        pass


class Number(Validator):
    """Number validator.

    `min`
        min of valid value.
    `max`
        max of valid value.
    """

    def __init__(self, min=None, max=None):
        super(Number, self).__init__(min, max)
        self.min = min
        self.max = max

    def validate(self, value):
        """Validate the value.

        :param value: String of a number.
        :raise InvalidValueError: `value` is invalid.
        """
        try:
            value = float(value)
        except ValueError, e:
            raise InvalidValueError(e)
        if self.max is not None:
            if not (value <= self.max):
                raise InvalidValueError('over max')
        if self.min is not None:
            if not (value >= self.min):
                raise InvalidValueError('less than min')


class FreeText(Validator):
    """Free text validator.
    
    `ban_phrases`
        List of ban phrase.
    
    `ignore_chars`
        List of ignore string.
        If ignore string is found in value, erase from the value 
        when before check ban phrases.
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
    
    `eq_value`
        If value is equal to `eq_value`, value is "valid". 
        
        Note: If *value* type is `str` and `eq_value` type is `unicode`, 
        the *value* to be decode as **UTF-8**.
    """

    def __init__(self, eq_value):
        super(Equal, self).__init__(eq_value)
        self.eq_value = eq_value

    def validate(self, value):
        if (not isinstance(value, basestring)) or \
                (not isinstance(self.eq_value, basestring)):
            if self.eq_value != value:
                raise InvalidValueError('%s is not equal' % value)
        elif isinstance(value, unicode):
            try:
                if isinstance(self.eq_value, unicode):
                    if self.eq_value != value:
                        raise InvalidValueError('%s is not equal' % value)
                elif self.eq_value.decode('utf-8') != value:
                    raise InvalidValueError('%s is not equal' % value)
            except UnicodeDecodeError, e:
                raise InvalidValueError(e)
        else:
            if isinstance(self.eq_value, unicode):
                try:
                    if self.eq_value != value.decode('utf-8'):
                        raise InvalidValueError('%s is not equal' % value)
                except UnicodeDecodeError, e:
                    raise InvalidValueError(e)
            elif self.eq_value != value:
                raise InvalidValueError('%s is not equal' % value)


class Regex(Validator):
    """Value validation by regexp.
    
    `regexp`
        Regular expression.
    
    `is_match`
        If True, use :func:`re.match`.
        Otherwise use :func:`re.search`.
        
        This flag is True by default.
    
    `flags`
        Sequence of flags.
        Acceptable types are: list, tuple, set, frozenset, basestring
        
        * "i": :data:`re.IGNORECASE`
        * "l": :data:`re.LOCALE`
        * "m": :data:`re.MULTILINE`
        * "s": :data:`re.DOTALL`
        * "u": :data:`re.UNICODE`
        * "x": :data:`re.VERBOSE`
    """

    def __init__(self, regexp, is_match=True, flags=None):
        if isinstance(regexp, basestring):
            self.regexp = regexp
        else:
            self.regexp = None
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
        if self.regexp is None:
            raise ValidationError('missing regexp')
        if not isinstance(value, basestring):
            raise InvalidTypeError('value is invalid')
        regex_method = re.match if self.is_match else re.search
        regex_result = regex_method(self.regexp, value)\
                if self.flags is None\
                else regex_method(self.regexp, value, self.flags)
        if regex_result is None:
            raise InvalidValueError('not found')


class AllowType(Validator):
    """Is TYPE allowed the value?
    
    `test_type`
        Callable.
        If raise exception when call this, value is "invalid".
    
    `on_exception`
        Exception callback.
        When call occurred exception by `test_type`.
        
        Callback function takes *one* argument, it is the exception object.
    """

    def __init__(self, test_type, on_exception=None):
        super(AllowType, self).__init__(test_type)
        self.test_type = test_type
        self.on_exception = on_exception

    def validate(self, value):
        if callable(self.test_type):
            try:
                self.test_type(value)
            except TypeError, e:
                raise InvalidTypeError(e)
            except Exception, e:
                if callable(self.on_exception):
                    self.on_exception(e)
                else:
                    raise InvalidValueError(e)
        else:
            raise ValidationError('type is invalid')


class Prefix(Validator):
    """Prefix validator.
    
    `prefix`
        If value that starts from `prefix`, evaluate the value as "valid".
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
    """Value type validator.
    
    `value_type`
        Expected type of the value.
    """

    def __init__(self, value_type):
        super(Type, self).__init__(value_type)
        self.value_type = value_type

    def validate(self, value):
        if not isinstance(value, self.value_type):
            raise InvalidTypeError('not same type')


class Length(Validator):
    """Limit length.
    
    `min`
        min length.
    `max`
        max length.
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
    
    usage:
        >>> console = Any(Equal('001'), Equal('101'))
        >>> model_number = Split(Equal('HVC'), console, sep='-')
        >>> model_number('HVC-001')
        >>> model_number('HVC-002')
        validators.ValidationError: 002 is not equal
    
    `*validators`
        Validator for splited values.
        
        Number of *validators* have to same as number of part of splited values.
    
    `sep`
        Value separator.
        
        Value will be split by this separator string.
    
    `rmatch`
        Right match flag.
        
        If this flag is :obj:`True`, to apply validator from *right side*. 
        Otherwise, to apply validator from *left side*.
        
        :obj:`False` by default.
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
            raise InvalidValueError('Number of splited value is mismatch.')
        for validator, token in itertools.izip(self.validators, splited):
            validator(token)


# derivative

class OnelinerText(FreeText):
    """Free text without linefeed code.
    
    Arguments are the same as :class:`~validators.FreeText`.
    """

    def __init__(self, ban_phrases=None, ignore_chars=None):
        ban = [u'\n']
        if isinstance(ban_phrases, list):
            ban.extend(ban_phrases)
        super(OnelinerText, self).__init__(
                ban_phrases=ban, ignore_chars=ignore_chars)


class String(Type):
    """String type only."""

    def __init__(self):
        super(String, self).__init__(basestring)


class Int(Type):
    """Int type only."""

    def __init__(self):
        super(Int, self).__init__(int)


class SortOrder(Any):
    """Sort order validator.
    
    Acceptable value:
        ``asc``:
            ascending order.
        ``desc``:
            descending order.
    """
    
    def __init__(self):
        super(SortOrder, self).__init__(Equal('asc'), Equal('desc')) 


class Flag(Any):
    """Flag validator."""

    def __init__(self):
        super(Flag, self).__init__(Equal(u'true'), Equal(u't'), Equal(u'1'),
                                   Equal(u'false'), Equal(u'f'), Equal(u'0'))

    def validate(self, value):
        super(Flag, self).validate(value.lower())


