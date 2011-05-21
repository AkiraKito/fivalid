# -*- coding: utf-8 -*-



import pickle
import hashlib
import re



class ValidationError(BaseException):
    pass



class BaseInterface(object):
    """Abstract validator base interface"""
    
    def __init__(self, *validators):
        self.validators = list(validators)
        self.__hash = hashlib.sha1(
            self.__class__.__name__ +\
            pickle.dumps(self.validators, pickle.HIGHEST_PROTOCOL)).digest()

    def __call__(self, value):
        raise NotImplementedError

    def __eq__(self, other):
        if self.ident == other.ident:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def ident(self):
        return self.__hash

    def add(self, other):
        if isinstance(other, BaseInterface):
            try:
                self.validators.append(other)
            except AttributeError:
                raise
        else:
            raise TypeError

    def remove(self, other):
        try:
            self.validators.remove(other)
        except ValueError:
            raise
        except AttributeError:
            raise


class All(BaseInterface):
    """AND operation for validators"""

    def __call__(self, value):
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError:
                raise


class Any(BaseInterface):
    """OR operation for validators"""

    def __call__(self, value):
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


class Validator(BaseInterface):
    """Validator base class"""

    def __init__(self, *args, **kwargs):
        self.__hash = hashlib.sha1(
            self.__class__.__name__ +\
            pickle.dumps(args, pickle.HIGHEST_PROTOCOL) +\
            pickle.dumps(kwargs, pickle.HIGHEST_PROTOCOL)).digest()

    def add(self, other):
        pass

    def remove(self, other):
        pass




# validator's children

class Number(Validator):
    """Number validator
    args:
        min: min of valid value.
        max: max of valid value.
    """

    def __init__(self, min=None, max=None):
        super(Number, self).__init__(min, max)
        self.min = min
        self.max = max

    def __call__(self, value):
        try:
            value = float(value)
        except ValueError:
            raise ValidationError
        if self.max is not None:
            if not (value <= self.max):
                raise ValidationError
        if self.min is not None:
            if not (value >= self.min):
                raise ValidationError


class FreeText(Validator):
    """Free text validator"""

    def __init__(self, ban_phrases=None, ignore_chars=None):
        super(FreeText, self).__init__(ban_phrases, ignore_chars)
        self.ban_phrases = list(ban_phrases) if ban_phrases is not None else []
        self.ignore_chars = list(ignore_chars) if ignore_chars is not None else []

    def __call__(self, value):
        if not isinstance(value, basestring):
            raise ValidationError
        for ignore in self.ignore_chars:
            value = re.sub(ignore, '', value)
        for phrase in self.ban_phrases:
            if re.search(phrase, value) is not None:
                raise ValidationError


class Equal(Validator):
    """Equal value validator"""

    def __init__(self, eq_value):
        super(Equal, self).__init__(eq_value)
        self.eq_value = eq_value

    def __call__(self, value):
        if (not isinstance(value, basestring)) or\
           (not isinstance(self.eq_value, basestring)):
            raise ValidationError
        if isinstance(value, unicode):
            if isinstance(self.eq_value, unicode):
                if self.eq_value != value:
                    raise ValidationError
            elif self.eq_value.decode('utf-8') != value:
                raise ValidationError
        else:
            if isinstance(self.eq_value, unicode):
                if self.eq_value != value.decode('utf-8'):
                    raise ValidationError
            elif self.eq_value != value:
                raise ValidationError


class Regex(Validator):
    """Value validation by regexp"""

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

    def __call__(self, value):
        if self.regexp is None:
            raise ValidationError
        regex_method = re.match if self.is_match else re.search
        if self.flags is None:
            if regex_method(self.regexp, value) is None:
                raise ValidationError
        else:
            if regex_method(self.regexp, value, self.flags) is None:
                raise ValidationError


class AllowType(Validator):
    """Is TYPE allowed the value?"""

    def __init__(self, test_type, on_exception=None):
        super(AllowType, self).__init__(test_type)
        self.test_type = test_type
        self.on_exception = on_exception

    def __call__(self, value):
        if callable(self.test_type):
            try:
                self.test_type(value)
            except TypeError:
                raise ValidationError
            except Exception, e:
                if callable(self.on_exception):
                    self.on_exception(e)
                else:
                    raise ValidationError
        else:
            raise ValidationError


class Prefix(Validator):

    def __init__(self, prefix):
        self.prefix = str(prefix)
        super(Prefix, self).__init__(prefix)

    def __call__(self, value):
        v = str(value)
        if not v.startswith(self.prefix):
            raise ValidationError


class Type(Validator):
    """Value type validator"""

    def __init__(self, value_type):
        super(Type, self).__init__(value_type)
        self.value_type = value_type

    def __call__(self, value):
        if not isinstance(value, self.value_type):
            raise ValidationError


class Length(Validator):
    """Limit length
    args:
        max: max length.
        min: min length.
    """

    def __init__(self, min=0, max=None):
        super(Length, self).__init__(max, min)
        self.max_length = max
        self.min_length = min if min >= 0 else 0

    def __call__(self, value):
        if self.max_length is not None:
            if not (len(value) <= int(self.max_length)):
                raise ValidationError
        if self.min_length >= 0:
            if not (len(value) >= int(self.min_length)):
                raise ValidationError




# derivative

class OnelinerText(FreeText):
    """Free text without linefeed code"""

    def __init__(self, ban_phrases=None, ignore_chars=None):
        ban = [u'\n']
        if isinstance(ban_phrases, list):
            ban.extend(ban_phrases)
        super(OnelinerText, self).__init__(ban_phrases=ban, ignore_chars=ignore_chars)


class String(Type):

    def __init__(self):
        super(String, self).__init__(basestring)


class Int(Type):

    def __init__(self):
        super(Int, self).__init__(int)


class SortOrder(Any):
    
    def __init__(self):
        super(SortOrder, self).__init__(Equal('asc'), Equal('desc')) 


class Flag(Any):

    def __init__(self):
        super(Flag, self).__init__(Equal(u'true'), Equal(u't'), Equal(u'1'),
                                   Equal(u'false'), Equal(u'f'), Equal(u'0'))

    def __call__(self, value):
        super(Flag, self).__call__(value.lower())

