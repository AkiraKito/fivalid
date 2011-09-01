# -*- coding: utf-8 -*-


from validators import ValidationError
from converters import ConversionError, unicode_converter


class RequiredError(BaseException):
    """`required` flag is True and missing input value in `field`."""
    pass

class MissingDefault(BaseException):
    pass



class BaseField(object):
    """Basic field validators and converter set.
    
    usage:
        >>> from validators import OnelinerText, Length, All
        >>> class NameField(BaseField):
        ...   validators = All(OnelinerText(), Length(max=10))
        ... 
        >>> field = NameField(required=True)
        >>> name = field()  # with required flag
        RequiredError
        >>> name = field('John Doeeeee')
        ValidationError
        >>> name = field('Jane Doe')
        >>> print name
        u'Jane Doe'
        >>> field = NameField()
        >>> print field()   # without required flag
        None
        >>> field('R2-D2')
        u'R2-D2'
        >>> 
    
    .. note::
        You have to set validator to :attr:`BaseField.validators`. Because default is :obj:`None`.
        
        :attr:`BaseField.converter` is :func:`converters.unicode_converter` by default.
    
    `default`
        Default value.
        If missing validatee value, to convert and return this value.
    
    `required`
        Required field flag.
        If this argument is *True* and default value is missing,
        raise :exc:`RequiredError`.
    
    `empty_value`
        Criterion value of *empty value*.
        
        If the same as given value as `empty_value` when validate one, 
        *given value* is treats as *empty*.
    
    `validators`
        If this argument was given, to replace default validators by one.
        
        A *instance* of subclass of :class:`~validators.ValidatorBaseInterface`.
    """

    validators = None
    converter = unicode_converter
    
    def __init__(self,
                 default=None,
                 required=False,
                 empty_value=None,
                 validators=None):
        self.empty_value = empty_value
        if validators is not None:
            self.validators = validators
        self.required = required 
        if default is None:
            self.default = default
        else:
            try:
                self.apply_validators(default)
            except (MissingDefault, ValueError):
                pass
            except ValidationError:
                raise
            else:
                self.default = default

    def __call__(self, value):
        """validate the value.
        
        :param value: validatee value.
        :raise ValidationError: value is invalid.
        :raise RequiredError: value and default-value are missing,
                              and required flag is True.
        :raise ConversionError: error occurred in converter.
        :return: If value and default-value are missing, return None.
                 otherwise, return a converted value.
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
        """apply validators to the value.
        
        :raise ValidationError: value is invalid.
        :raise MissingDefault: value and default-value are missing.
        :raise ValueError: value is missing, but default-value is available.
        """
        if value != self.empty_value:
            try:
                self.validators(value)
            except ValidationError:
                raise
        else:
            # value is empty
            if getattr(self, 'default', None) is None:  # default-value was changed in init?
                # value and default-value are missing
                raise MissingDefault
            else:
                # value is missing, but default_value is available
                raise ValueError



