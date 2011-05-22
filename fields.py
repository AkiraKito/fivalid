# -*- coding: utf-8 -*-


from validators import ValidationError
from converters import ConversionError, unicode_converter


class RequiredError(BaseException):
    pass

class MissingDefault(BaseException):
    pass



class BaseField(object):

    validators = None
    converter = unicode_converter
    
    def __init__(self, default=None, required=False, empty_value=None, validators=None):
        self.empty_value = empty_value
        if validators is not None:
            self.validators = validators
        self.required = required 
        self.default = ''
        try:
            self.apply_validators(default)
        except (MissingDefault, ValueError):
            pass
        except ValidationError:
            raise
        else:
            self.default = default

    def __call__(self, value):
        """validate the value
        raises:
            ValidationError: value is invalid.
            RequiredError: value and default-value are missing, and required flag is True.
            ConversionError: error occurred in converter.
        return:
            None: value and default-value are missing.
            other: converted value.
        """
        try:
            self.apply_validators(value)
        except MissingDefault:
            if self.required:
                raise RequiredError
            else:
                return None
        except ValueError:
            return self.converter(self.default)
        return self.converter(value)
    
    def apply_validators(self, value):
        """apply validators to the value
        raises:
            ValidationError: value is invalid.
            MissingDefault: value and default-value are missing.
            ValueError: value is missing, but default-value is available.
        """
        if value != self.empty_value:
            try:
                self.validators(value)
            except ValidationError:
                raise
        elif self.default is None:
            # value and default-value are missing
            raise MissingDefault
        else:
            # value is missing, but default_value is available
            raise ValueError




