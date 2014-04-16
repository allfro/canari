# !/usr/bin/env python

from canari.xmltools.oxml import MaltegoElement, fields as fields_

from datetime import datetime, date, timedelta
from numbers import Number
import re


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.5'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'MaltegoException',
    'MaltegoTransformExceptionMessage',
    'MaltegoTransformRequestMessage',
    'Label',
    'MatchingRule',
    'Field',
    'UIMessageType',
    'UIMessage',
    'MaltegoTransformResponseMessage',
    'MaltegoMessage',
    'StringEntityField',
    'EnumEntityField',
    'IntegerEntityField',
    'BooleanEntityField',
    'FloatEntityField',
    'LongEntityField',
    'DateTimeEntityField',
    'DateEntityField',
    'timespan',
    'TimeSpanEntityField',
    'RegexEntityField',
    'ColorEntityField',
    'EntityFieldType',
    'EntityField',
    'EntityLinkField',
    'Entity',
]


class MaltegoException(MaltegoElement, Exception):
    class meta:
        tagname = 'Exception'

    def __init__(self, value):
        super(MaltegoElement, self).__init__(value=value)

    value = fields_.String(tagname='.')


class MaltegoTransformExceptionMessage(MaltegoElement):
    exceptions = fields_.List(MaltegoException, tagname='Exceptions')

    def appendelement(self, exception):
        if isinstance(exception, MaltegoException):
            self.exceptions.append(exception)
        else:
            self.exceptions.append(MaltegoException(str(exception)))


class Limits(MaltegoElement):
    soft = fields_.Integer(attrname='SoftLimit', default=500)
    hard = fields_.Integer(attrname='HardLimit', default=10000)


class Label(MaltegoElement):
    def __init__(self, name=None, value=None, **kwargs):
        super(Label, self).__init__(name=name, value=value, **kwargs)

    value = fields_.CDATA(tagname='.')
    type = fields_.String(attrname='Type', default='text/text')
    name = fields_.String(attrname='Name')


class MatchingRule(object):
    Strict = "strict"
    Loose = "loose"


class Field(MaltegoElement):
    def __init__(self, name=None, value=None, **kwargs):
        super(Field, self).__init__(name=name, value=value, **kwargs)

    name = fields_.String(attrname='Name')
    displayname = fields_.String(attrname='DisplayName', required=False)
    matchingrule = fields_.String(attrname='MatchingRule', default=MatchingRule.Strict, required=False)
    value = fields_.String(tagname='.')


class _Entity(MaltegoElement):
    class meta:
        tagname = 'Entity'

    type = fields_.String(attrname='Type')
    fields = fields_.Dict(Field, key='name', tagname='AdditionalFields', required=False)
    labels = fields_.Dict(Label, key='name', tagname='DisplayInformation', required=False)
    value = fields_.String(tagname='Value')
    weight = fields_.Integer(tagname='Weight', default=1)
    iconurl = fields_.String(tagname='IconURL', required=False)

    def appendelement(self, other):
        if isinstance(other, Field):
            self.fields.append(other)
        elif isinstance(other, Label):
            self.labels.append(other)

    def removeelement(self, other):
        if isinstance(other, Field):
            self.fields.remove(other)
        elif isinstance(other, Label):
            self.labels.remove(other)


class UIMessageType:
    Fatal = "FatalError"
    Partial = "PartialError"
    Inform = "Inform"
    Debug = "Debug"


class UIMessage(MaltegoElement):
    def __init__(self, value=None, **kwargs):
        super(UIMessage, self).__init__(value=value, **kwargs)

    type = fields_.String(attrname='MessageType', default=UIMessageType.Inform)
    value = fields_.String(tagname='.')


class MaltegoTransformResponseMessage(MaltegoElement):
    uimessages = fields_.List(UIMessage, tagname='UIMessages')
    entities = fields_.List(_Entity, tagname='Entities')

    def appendelement(self, other):
        if isinstance(other, Entity):
            self.entities.append(other.__entity__)
        elif isinstance(other, _Entity):
            self.entities.append(other)
        elif isinstance(other, UIMessage):
            self.uimessages.append(other)

    def removeelement(self, other):
        if isinstance(other, Entity):
            self.entities.remove(other.__entity__)
        elif isinstance(other, _Entity):
            self.entities.append(other)
        elif isinstance(other, UIMessage):
            self.uimessages.remove(other)


class StringEntityField(object):
    def __init__(self, name, displayname=None, decorator=None, matchingrule=MatchingRule.Strict, is_value=False,
                 **extras):
        self.decorator = decorator
        self.is_value = is_value
        self.name = name
        self.displayname = displayname
        self.matchingrule = matchingrule

    def __get__(self, obj, objtype):
        if self.is_value:
            return obj.value
        elif self.name in obj.fields:
            return obj.fields[self.name].value
        return None

    def __set__(self, obj, val):
        if self.is_value:
            obj.value = val
        elif not val and self.name in obj.fields:
            del obj.fields[self.name]
        else:
            if self.name not in obj.fields:
                obj.fields[self.name] = Field(
                    name=self.name,
                    value=val,
                    displayname=self.displayname,
                    matchingrule=self.matchingrule
                )
            else:
                obj.fields[self.name].value = val
        if callable(self.decorator):
            self.decorator(obj, val)


class EnumEntityField(StringEntityField):
    def __init__(self, name, displayname=None, choices=None, decorator=None, matchingrule=MatchingRule.Strict,
                 is_value=False, **extras):
        self.choices = [str(c) if not isinstance(c, basestring) else c for c in choices or []]
        super(EnumEntityField, self).__init__(name, displayname, decorator, matchingrule, is_value)

    def __set__(self, obj, val):
        val = str(val) if not isinstance(val, basestring) else val
        if val not in self.choices:
            raise ValueError('Expected one of %s (got %s instead)' % (self.choices, val))
        super(EnumEntityField, self).__set__(obj, val)


class IntegerEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        i = super(IntegerEntityField, self).__get__(obj, objtype)
        return int(i) if i is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of int (got %s instance instead)' % type(val).__name__)
        super(IntegerEntityField, self).__set__(obj, val)


class BooleanEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        b = super(BooleanEntityField, self).__get__(obj, objtype)
        return b.startswith('t') or b == '1' if b is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, bool):
            raise TypeError('Expected an instance of bool (got %s instance instead)' % type(val).__name__)
        super(BooleanEntityField, self).__set__(obj, str(val).lower())


class FloatEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        f = super(FloatEntityField, self).__get__(obj, objtype)
        return float(f) if f is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of float (got %s instance instead)' % type(val).__name__)
        super(FloatEntityField, self).__set__(obj, val)


class LongEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        l = super(LongEntityField, self).__get__(obj, objtype)
        return long(l) if l is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of float (got %s instance instead)' % type(val).__name__)
        super(LongEntityField, self).__set__(obj, val)


class DateTimeEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        d = super(DateTimeEntityField, self).__get__(obj, objtype)
        return datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f') if d is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, datetime):
            raise TypeError('Expected an instance of datetime (got %s instance instead)' % type(val).__name__)
        super(DateTimeEntityField, self).__set__(obj, val)


class DateEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        d = super(DateEntityField, self).__get__(obj, objtype)
        return datetime.strptime(d, '%Y-%m-%d').date() if d is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, date):
            raise TypeError('Expected an instance of date (got %s instance instead)' % type(val).__name__)
        super(DateEntityField, self).__set__(obj, val)


class timespan(timedelta):
    matcher = re.compile('(\d+)d (\d+)h(\d+)m(\d+)\.(\d+)s')

    def __str__(self):
        return '%dd %dh%dm%d.%03ds' % (
            abs(self.days),
            int(self.seconds) // 3600,
            int(self.seconds) % 3600 // 60,
            int(self.seconds) % 60,
            int(self.microseconds)
        )

    @classmethod
    def fromstring(cls, ts):
        m = cls.matcher.match(ts)
        if m is None:
            raise ValueError('Time span must be in "%%dd %%Hh%%Mm%%S.%%fs" format')
        days, hours, minutes, seconds, useconds = [int(i) for i in m.groups()]
        return timespan(days, (hours * 3600) + (minutes * 60) + seconds, useconds)


class TimeSpanEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        d = super(TimeSpanEntityField, self).__get__(obj, objtype)
        return timespan.fromstring(d) if d is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, timespan) or not isinstance(val, timedelta):
            raise TypeError('Expected an instance of timedelta (got %s instance instead)' % type(val).__name__)
        if val.__class__ is timedelta:
            val = timespan(val.days, val.seconds, val.microseconds)
        super(TimeSpanEntityField, self).__set__(obj, val)


class RegexEntityField(StringEntityField):
    def __init__(self, name, displayname=None, pattern='.*', decorator=None, matchingrule=MatchingRule.Strict,
                 is_value=False, **extras):
        super(RegexEntityField, self).__init__(name, displayname, decorator, matchingrule, is_value, **extras)
        self.pattern = re.compile(pattern)

    def __set__(self, obj, val):
        if not isinstance(val, basestring):
            val = str(val)
        if not self.pattern.match(val):
            raise ValueError('Failed match for %s, expected pattern %s instead.' % (
                repr(val), repr(self.pattern.pattern))
            )
        super(RegexEntityField, self).__set__(obj, val)


class ColorEntityField(RegexEntityField):
    def __init__(self, name, displayname=None, decorator=None, matchingrule=MatchingRule.Strict, is_value=False,
                 **extras):
        super(ColorEntityField, self).__init__(name, displayname, '^#[0-9a-fA-F]{6}$', decorator, matchingrule,
                                               is_value, **extras)


class EntityFieldType:
    String = StringEntityField
    Integer = IntegerEntityField
    Long = LongEntityField
    Float = FloatEntityField
    Bool = BooleanEntityField
    Enum = EnumEntityField
    Date = DateEntityField
    DateTime = DateTimeEntityField
    TimeSpan = TimeSpanEntityField
    Color = ColorEntityField


class EntityField(object):
    def __init__(self, link=False, **kwargs):
        self.name = kwargs.pop('name')
        if self.name is None:
            raise ValueError("Keyword argument 'name' is required.")
        self.property = kwargs.pop('propname', re.sub('[^\w]+', '_', self.name))
        if not link:
            self.displayname = kwargs.pop('displayname', self.name.title())
        else:
            self.displayname = kwargs.pop('displayname', None)
        self.type = kwargs.pop('type', EntityFieldType.String)
        self.required = kwargs.pop('required', False)
        self.matchingrule = kwargs.pop('matchingrule', MatchingRule.Strict)
        self.decorator = kwargs.pop('decorator', None)
        self.is_value = kwargs.pop('is_value', False)
        self.extras = kwargs

    def __call__(self, cls):
        setattr(
            cls,
            self.property,
            self.type(
                name=self.name,
                displayname=self.displayname,
                decorator=self.decorator,
                matchingrule=self.matchingrule,
                is_value=self.is_value,
                **self.extras
            )
        )
        cls._fields_to_properties_[self.name] = self.property
        return cls


class EntityLinkField(EntityField):
    def __init__(self, **kwargs):
        kwargs['name'] = 'link#%s' % kwargs.get('name')
        super(EntityLinkField, self).__init__(link=True, **kwargs)


class MetaEntityClass(type):
    registry = {}

    def __new__(cls, clsname, bases, attrs):
        if '_fields_to_properties_' not in attrs:
            attrs['_fields_to_properties_'] = {}
        if '_name_' not in attrs:
            attrs['_name_'] = clsname
        if '_v2type_' not in attrs:
            attrs['_v2type_'] = clsname
        new_cls = super(cls, MetaEntityClass).__new__(cls, clsname, bases, attrs)
        new_cls._type_ = '%s.%s' % (new_cls._namespace_, new_cls._name_)
        for base in bases:
            if '_fields_to_properties_' in base.__dict__:
                attrs['_fields_to_properties_'].update(base._fields_to_properties_)
        MetaEntityClass.registry[new_cls._type_] = new_cls
        MetaEntityClass.registry[new_cls._v2type_] = new_cls
        return new_cls

    @staticmethod
    def to_entity_type(entity_type_str):
        if entity_type_str in MetaEntityClass.registry:
            return MetaEntityClass.registry.get(entity_type_str)
        return MetaEntityClass.registry[None]


@EntityField(name='notes#', propname='notes', link=True, matchingrule=MatchingRule.Loose)
@EntityField(name='bookmark#', propname='bookmark', type=EntityFieldType.Integer, matchingrule=MatchingRule.Loose,
             link=True)
@EntityLinkField(name='maltego.link.label', propname='linklabel', matchingrule=MatchingRule.Loose)
@EntityLinkField(name='maltego.link.style', propname='linkstyle', matchingrule=MatchingRule.Loose,
                 type=EntityFieldType.Integer)
@EntityLinkField(name='maltego.link.show-label', propname='linkshowlabel', matchingrule=MatchingRule.Loose,
                 type=EntityFieldType.Enum, choices=[0, 1])
@EntityLinkField(name='maltego.link.color', propname='linkcolor', matchingrule=MatchingRule.Loose)
@EntityLinkField(name='maltego.link.thickness', propname='linkthickness', matchingrule=MatchingRule.Loose,
                 type=EntityFieldType.Integer)
class Entity(object):
    __metaclass__ = MetaEntityClass
    _namespace_ = 'maltego'
    _name_ = None
    _v2type_ = None
    _fields_to_properties_ = {}

    def __init__(self, value, **kwargs):
        if isinstance(value, _Entity):
            self._entity = value
            # for name, field in self._entity.fields.iteritems():
            #     if name not in self._fields_to_properties_:
            #         self._bind_field(field)
        else:
            self._entity = _Entity(
                type=kwargs.pop('type', self._type_),
                value=value,
                weight=kwargs.pop('weight', None),
                iconurl=kwargs.pop('iconurl', None),
                fields=kwargs.pop('fields', None),
                labels=kwargs.pop('labels', None)
            )
        self._value_property = None
        for p in kwargs:
            if hasattr(self, p):
                setattr(self, p, kwargs[p])

    # def _bind_field(self, field):
    #     EntityField(
    #         **dict(
    #             (f.field_name, getattr(field, f.field_name)) for f in field._fields
    #         )
    #     ).__call__(self.__class__)
    #     return re.sub('[^\w]+', '_', field.name)


    def appendelement(self, other):
        if isinstance(other, Field):
            if other.name not in self._fields_to_properties_:
                # propname = self._bind_field(other)
                self.fields[other.name] = other
            else:
                propname = self._fields_to_properties_[other.name]
                setattr(self, propname, other.value)
                # setattr(self, propname, other.value)
        elif isinstance(other, Label):
            self.labels[other.name] = other

    def removeelement(self, other):
        if isinstance(other, Field) and other.name in self.fields:
            del self.fields[other.name]
        elif isinstance(other, Label) and other.name in self.labels:
            del self.labels[other.name]

    @property
    def __fields__(self):
        return tuple(set(self._fields_to_properties_.values()))

    @property
    def __entity__(self):
        return self._entity

    @property
    def __type__(self):
        return self._type_

    def set_field(self, name, value):
        if name not in self._fields_to_properties_:
            self.appendelement(Field(name, value))
        setattr(self, self._fields_to_properties_[name], value)

    def get_field(self, name):
        if name not in self._fields_to_properties_:
            raise KeyError('No such field: %s.' % repr(name))
        return getattr(self, self._fields_to_properties_[name])

    def __getitem__(self, item):
        if isinstance(item, basestring):
            return self.get_field(item)
        raise TypeError('Entity indices must be str, not %s' % type(item).__name__)

    def __setitem__(self, key, value):
        if isinstance(key, basestring):
            self.set_field(key, value)
        else:
            raise TypeError('Entity indices must be str, not %s' % type(value).__name__)

    def __add__(self, other):
        return self.__iadd__(other)

    def __iadd__(self, other):
        if isinstance(other, list):
            for o in other:
                self.appendelement(o)
        else:
            self.appendelement(other)
        return self

    appendelements = __iadd__

    def __sub__(self, other):
        return self.__isub__(other)

    def __isub__(self, other):
        if isinstance(other, list):
            for o in other:
                self.removeelement(o)
        else:
            self.removeelement(other)
        return self

    removeelements = __isub__

    def __eq__(self, other):
        return self.render() == other.render()

    def __getattr__(self, item):
        return getattr(self._entity, item)

    def __setattr__(self, key, value):
        if key in ['value', 'iconurl', 'weight', 'type']:
            setattr(self._entity, key, value)
        return object.__setattr__(self, key, value)


class MaltegoTransformRequestMessage(MaltegoElement):
    entities = fields_.List(_Entity, tagname='Entities', required=False)
    parameters = fields_.Dict(Field, tagname='TransformFields', key='name', required=False)
    limits = fields_.Model(Limits, required=False)

    def __init__(self, **kwargs):
        super(MaltegoTransformRequestMessage, self).__init__(**kwargs)
        self._canari_fields = dict([(f.name, f.value) for f in self.entity.fields.values()])

    @property
    def entity(self):
        if self.entities:
            return MetaEntityClass.to_entity_type(self.entities[0].type)(self.entities[0])
        return Entity('')

    @property
    def params(self):
        if 'canari.local.arguments' in self.parameters:
            return self.parameters['canari.local.arguments'].value
        return self.parameters

    @property
    def value(self):
        return self.entity.value

    @property
    def fields(self):
        return self._canari_fields


class MaltegoMessage(MaltegoElement):
    message = fields_.Choice(
        fields_.Model(MaltegoTransformExceptionMessage),
        fields_.Model(MaltegoTransformResponseMessage),
        fields_.Model(MaltegoTransformRequestMessage)
    )