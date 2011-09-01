# -*- coding: utf-8 -*-

"""
    field-value converter
    
    args:
        field:
            The reference to subclass of BaseField instance object.
        value:
            Value that will be converted.
    return:
        The converted value.
"""


class ConversionError(BaseException):
    """Error occurred while value conversion."""
    pass


def unicode_converter(field, value):
    """Unicode converter.
    
    :param field: Reference to subclass of BaseField instance object.
    :param value: Will convert value.
    :raise ConversionError: Failed to convert the value.
    :rtype: Python :obj:`unicode`.
    """
    try:
        return unicode(value)
    except UnicodeDecodeError, e:
        for enc in ('utf-8', 'cp932'):
            try:
                return unicode(value.decode(enc))
            except UnicodeDecodeError:
                continue
        raise ConversionError(e)
    except Exception, e:
        raise ConversionError(e)


def float_converter(field, value):
    """Float converter.
    
    :param field: Reference to subclass of BaseField instance object.
    :param value: Will convert value.
    :raise ConversionError: Failed to convert the value.
    :rtype: Python :obj:`float`.
    """
    try:
        converted = float(value)
    except ValueError, e:
        raise ConversionError(e)
    return converted


def int_converter(field, value):
    """Int converter.
    
    :param field: Reference to subclass of BaseField instance object.
    :param value: Will convert value.
    :raise ConversionError: Failed to convert the value.
    :rtype: Python :obj:`int`.
    """
    try:
        converted = int(value)
    except ValueError, e:
        raise ConversionError(e)
    return converted


def truthvalue_converter(field, value):
    """Truth value converter.
    
    :param field: Reference to subclass of BaseField instance object.
    :param value: "true"(ignore case), "t"(ignore case), "1", and other *True* object 
                  that eval from :obj:`bool` is :obj:`True`. 
                  "false"(ignore case), "f"(ignore case), "0", and other *False* object
                  that eval from :obj:`bool` is :obj:`False`.
    :rtype: Python :obj:`bool`.
    """
    if isinstance(value, basestring):
        v = value.lower()
        if v in ('true', 't', '1'):
            return True
        if v in ('false', 'f', '0'):
            return False
    return bool(value)


def colon_separated_converter(field, value):
    """Colon separated value conveter.
    
    :param field: Reference to subclass of BaseField instance object.
    :param value: Colon(":") separated string.
    :raise ConversionError: Failed to convert the value.
    :return: :obj:`tuple` of before-value and behind-value.
    """
    try:
        value_a, value_b = value.split(':')
    except ValueError, e:
        raise ConversionError(e)
    except AttributeError:
        raise ConversionError('value is not string object.')
    return (value_a, value_b)


