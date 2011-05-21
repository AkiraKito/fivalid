# -*- coding: utf-8 -*-

# field-value converter
# args:
#   field: reference to subclass of BaseField instance object
#   value: to convert value; normally string object
# return:
#   the converted value


class ConversionError(BaseException):
    pass


def unicode_converter(field, value):
    try:
        return unicode(value)
    except UnicodeDecodeError:
        for enc in ('utf-8', 'cp932'):
            try:
                return unicode(value.decode(enc))
            except UnicodeDecodeError:
                pass
        raise ConversionError
    except:
        raise ConversionError


def float_converter(field, value):
    try:
        converted = float(value)
    except ValueError:
        raise ConversionError
    return converted


def int_converter(field, value):
    try:
        converted = int(value)
    except ValueError:
        raise ConversionError
    return converted


def truthvalue_converter(field, value):
    v = value.lower()
    if v == 'true' or v == 't' or v == '1':
        return True
    elif v == 'false' or v == 'f' or v == '0':
        return False
    else:
        raise ConversionError


def colon_separated_converter(field, value):
    try:
        value_a, value_b = value.split(':')
    except ValueError:
        raise ConversionError
    return (value_a, value_b)



