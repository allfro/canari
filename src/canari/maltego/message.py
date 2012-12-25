#!/usr/bin/env python

from canari.xmltools.oxml import *

from numbers import Number
from re import sub


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'Message',
    'MaltegoElement',
    'MaltegoMessage',
    'MaltegoTransformExceptionMessage',
    'MaltegoException',
    'MaltegoTransformResponseMessage',
    'Label',
    'MatchingRule',
    'Field',
    'StringEntityField',
    'EnumEntityField',
    'IntegerEntityField',
    'BooleanEntityField',
    'FloatEntityField',
    'LongEntityField',
    'EntityFieldType',
    'EntityField',
    'UIMessageType',
    'UIMessage',
    'Entity',
]


class Message(ElementTree):
    pass


class MaltegoElement(Element):
    pass


class MaltegoMessage(MaltegoElement):

    def __init__(self, message):
        super(MaltegoMessage, self).__init__(self.__class__.__name__)
        self.append(message)


@XMLSubElement(name='Exceptions', propname='exceptions', type=XSSubElementType.List)
class MaltegoTransformExceptionMessage(MaltegoElement):

    def __init__(self, **kwargs):
        super(MaltegoTransformExceptionMessage, self).__init__(self.__class__.__name__)
        self.appendelements(kwargs.get('exceptions'))

    def appendelement(self, exception):
        if isinstance(exception, MaltegoException):
            self.exceptions += exception
        else:
            self.exceptions += MaltegoException(str(exception))


class MaltegoException(MaltegoElement, Exception):

    def __init__(self, message):
        super(MaltegoException, self).__init__('Exception')
        Exception.__init__(self, message)
        self.text = message if not isinstance(message, basestring) else message


@XMLSubElement(name='UIMessages', propname='uimessages', type=XSSubElementType.List)
@XMLSubElement(name='Entities', propname='entities', type=XSSubElementType.List)
class MaltegoTransformResponseMessage(MaltegoElement):

    def __init__(self, **kwargs):
        super(MaltegoTransformResponseMessage, self).__init__(self.__class__.__name__)
        self.appendelements(kwargs.get('entities'))
        self.appendelements(kwargs.get('uimessages'))

    def appendelement(self, other):
        if isinstance(other, Entity):
            self.entities += other
        elif isinstance(other, UIMessage):
            self.uimessages += other

    def removeelement(self, other):
        if isinstance(other, Entity):
            self.entities -= other
        elif isinstance(other, UIMessage):
            self.uimessages -= other


@XMLAttribute(name='Name', propname='name')
@XMLAttribute(name='Type', propname='type', default='text/text')
@XMLSubElement(name='CDATA', propname='cdata')
class Label(MaltegoElement):

    def __init__(self, name, value, **kwargs):
        super(Label, self).__init__(self.__class__.__name__)
        self.name = name
        self.type = kwargs.get('type', self.type)

        if self.type == 'text/html':
            self.cdata = value
        else:
            self.text = str(value) if not isinstance(value, basestring) else value


class MatchingRule(object):
    Strict = "strict"
    Loose = "loose"


@XMLAttribute(name='Name', propname='name')
@XMLAttribute(name='DisplayName', propname='displayname')
@XMLAttribute(name='MatchingRule', propname='matchingrule', default=MatchingRule.Strict)
class Field(MaltegoElement):

    def __init__(self, name, value, **kwargs):
        super(Field, self).__init__(self.__class__.__name__)
        self.name = name
        self.matchingrule = kwargs.get('matchingrule', self.matchingrule)
        self.displayname = kwargs.get('displayname', None)
        self.text = str(value) if not isinstance(value, basestring) else value


class StringEntityField(object):

    def __init__(self, name, displayname=None, decorator=None, matchingrule=MatchingRule.Strict):
        self.name = name
        self.displayname = displayname
        self.decorator = decorator
        self.matchingrule = matchingrule

    def _find(self, obj):
        for f in obj.fields:
            if f.name == self.name:
                return f
        return None

    def __get__(self, obj, objtype):
        o = self._find(obj)
        return o.text if o is not None else None

    def __set__(self, obj, val):
        f = self._find(obj)
        if not isinstance(val, basestring) and val is not None:
            val = str(val)
        if f is None and val is not None:
            f = Field(self.name, val, displayname=self.displayname, matchingrule=self.matchingrule)
            obj += f
        elif f is not None and val is None:
            obj -= f
        else:
            f.text = val
        if self.decorator is not None:
            self.decorator(obj, val)


class EnumEntityField(StringEntityField):

    def __init__(self, name, displayname=None, choices=[], decorator=None, matchingrule=MatchingRule.Strict):
        self.choices = [ str(c) if not isinstance(c, basestring) else c for c in choices ]
        super(EnumEntityField, self).__init__(name, displayname, decorator, matchingrule)

    def __set__(self, obj, val):
        val = str(val) if not isinstance(val, basestring) else val
        if val not in self.choices:
            raise ValueError('Expected one of %s (got %s instead)' % (self.choices, val))
        super(EnumEntityField, self).__set__(obj, val)


class IntegerEntityField(StringEntityField):

    def __get__(self, obj, objtype):
        return int(super(IntegerEntityField, self).__get__(obj, objtype))

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of int (got %s instance instead)' % type(val).__name__)
        super(IntegerEntityField, self).__set__(obj, val)


class BooleanEntityField(StringEntityField):

    def __get__(self, obj, objtype):
        return super(BooleanEntityField, self).__get__(obj, objtype) == 'true'

    def __set__(self, obj, val):
        if not isinstance(val, bool):
            raise TypeError('Expected an instance of bool (got %s instance instead)' % type(val).__name__)
        super(BooleanEntityField, self).__set__(obj, str(val).lower())


class FloatEntityField(StringEntityField):

    def __get__(self, obj, objtype):
        return float(super(FloatEntityField, self).__get__(obj, objtype))

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of float (got %s instance instead)' % type(val).__name__)
        super(FloatEntityField, self).__set__(obj, val)


class LongEntityField(StringEntityField):

    def __get__(self, obj, objtype):
        return long(super(LongEntityField, self).__get__(obj, objtype))

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of float (got %s instance instead)' % type(val).__name__)
        super(LongEntityField, self).__set__(obj, val)


class EntityFieldType(object):
    String = StringEntityField
    Integer = IntegerEntityField
    Long = LongEntityField
    Float = FloatEntityField
    Bool = BooleanEntityField
    Enum = EnumEntityField


class EntityField(object):

    def __init__(self, link=False, **kwargs):
        self.name = kwargs.get('name')
        if self.name is None:
            raise ValueError("Keyword argument 'name' is required.")
        self.property = kwargs.get('propname', sub('[^\w]+', '_', self.name))
        if not link:
            self.displayname = kwargs.get('displayname', self.name.title())
        else:
            self.displayname = kwargs.get('displayname', None)
        self.type = kwargs.get('type', EntityFieldType.String)
        self.required = kwargs.get('required', False)
        self.choices = kwargs.get('choices')
        self.matchingrule = kwargs.get('matchingrule', MatchingRule.Strict)
        self.decorator = kwargs.get('decorator')

    def __call__(self, cls):
        if self.type is EntityFieldType.Enum:
            setattr(
                cls,
                self.property,
                self.type(self.name, self.displayname, self.choices, self.decorator, self.matchingrule)
            )
        else:
            setattr(
                cls,
                self.property,
                self.type(self.name, self.displayname, self.decorator, self.matchingrule)
            )
        return cls


class EntityLinkField(EntityField):

    def __init__(self, **kwargs):
        kwargs['name'] = 'link#%s' % kwargs.get('name')
        super(EntityLinkField, self).__init__(link=True, **kwargs)


class UIMessageType(object):
    Fatal = "FatalError"
    Partial = "PartialError"
    Inform = "Inform"
    Debug = "Debug"


@XMLAttribute(name='MessageType', propname='type', default=UIMessageType.Inform)
class UIMessage(MaltegoElement):

    def __init__(self, message, **kwargs):
        super(UIMessage, self).__init__(self.__class__.__name__)
        self.type = kwargs.get('type', self.type)
        self.text = str(message) if not isinstance(message, basestring) else message


@XMLSubElement(name='Value', propname='value')
@XMLSubElement(name='Weight', propname='weight', type=XSSubElementType.Integer, default=1)
@XMLSubElement(name='IconURL', propname='iconurl')
@XMLSubElement(name='AdditionalFields', propname='fields', type=XSSubElementType.List)
@XMLSubElement(name='DisplayInformation', propname='labels', type=XSSubElementType.List)
@XMLSubElement(name='Value', propname='value')
@XMLAttribute(name='Type', propname='type')
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
class Entity(MaltegoElement):

    namespace = 'maltego'
    name = None

    def __init__(self, value, **kwargs):
        super(Entity, self).__init__("Entity")
        type = kwargs.pop('type', None)
        if type is None:
            self.type = '%s.%s' % (self.namespace, (self.__class__.__name__ if self.name is None else self.name))
        else:
            self.type = type
        self.value = value
        self.weight = kwargs.pop('weight', self.weight)
        self.iconurl = kwargs.pop('iconurl', self.iconurl)
        self.appendelements(kwargs.pop('fields', None))
        self.appendelements(kwargs.pop('labels', None))
        for p in kwargs:
            if hasattr(self, p):
                setattr(self, p, kwargs[p])

    def appendelement(self, other):
        if isinstance(other, Field):
#            display_name = other.get('DisplayName')
#            if display_name is None:
#                name = other.get('Name')
#                if name in self.fields.keys():
#                    other.set('DisplayName', self.fields[name])
            self.fields += other
        elif isinstance(other, Label):
            self.labels += other

    def removeelement(self, other):
        if isinstance(other, Field):
            self.fields -= other
        elif isinstance(other, Label):
            self.labels -= other





