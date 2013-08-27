#!/usr/bin/env python
import time

from canari.xmltools.oxml import XMLAttribute, XSAttributeType, XMLSubElement, XSSubElementType
from message import MaltegoElement


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'BuiltInTransformSets',
    'TransformAdapter',
    'MaltegoTransform',
    'InputConstraint',
    'OutputEntity',
    'InputEntity',
    'PropertyType',
    'TransformProperty',
    'TransformPropertySetting',
    'CmdLineTransformProperty',
    'CmdLineTransformPropertySetting',
    'CmdParmTransformProperty',
    'CmdParmTransformPropertySetting',
    'CmdCwdTransformProperty',
    'CmdCwdTransformPropertySetting',
    'CmdDbgTransformProperty',
    'CmdDbgTransformPropertySetting',
    'TransformSettings',
    'Set',
    'MaltegoServer',
    'Authentication',
    'Protocol'
]


class TransformAdapter(object):
    Local = 'com.paterva.maltego.transform.protocol.v2.LocalTransformAdapterV2'
    Remote = 'com.paterva.maltego.transform.protocol.v2.RemoteTransformAdapterV2'


@XMLAttribute(name='abstract', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='author', default='')
@XMLAttribute(name='description', default='')
@XMLAttribute(name='displayName', propname='displayname')
@XMLAttribute(name='name')
@XMLAttribute(name='requireDisplayInfo', propname='requireinfo', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='template', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='visibility', default='public')
@XMLAttribute(name='helpURL', propname='helpurl')
@XMLAttribute(name='owner')
@XMLAttribute(name='version', default='1.0')
@XMLAttribute(name='locationRelevance', propname='locrel')
@XMLSubElement(name='TransformAdapter', propname='adapter', type=XSSubElementType.Enum, choices=[TransformAdapter.Local, TransformAdapter.Remote], default=TransformAdapter.Local)
@XMLSubElement(name='StealthLevel', propname='stealthlvl', type=XSSubElementType.Integer, default=0)
@XMLSubElement(name='defaultSets', propname='sets', type=XSSubElementType.List)
@XMLSubElement(name='Disclaimer', propname='disclaimer', type=XSSubElementType.CData)
@XMLSubElement(name='Help', propname='help', type=XSSubElementType.CData)
@XMLSubElement(name='OutputEntities', propname='output', type=XSSubElementType.List)
@XMLSubElement(name='InputConstraints', propname='input', type=XSSubElementType.List)
@XMLSubElement(name='Properties/Fields', propname='properties', type=XSSubElementType.List)
class MaltegoTransform(MaltegoElement):
    def __init__(self, name, displayname, **kwargs):
        super(MaltegoTransform, self).__init__(self.__class__.__name__)
        self.name = name
        self.displayname = displayname
        self.abstract = kwargs.get('abstract', self.abstract)
        self.author = kwargs.get('author', self.author)
        self.description = kwargs.get('description', self.description)
        self.requireinfo = kwargs.get('requireinfo', self.requireinfo)
        self.template = kwargs.get('template', self.template)
        self.visibility = kwargs.get('visibility', self.visibility)
        self.helpurl = kwargs.get('helpurl', self.helpurl)
        self.owner = kwargs.get('owner', self.owner)
        self.version = kwargs.get('version', self.version)
        self.locrel = kwargs.get('locrel', self.locrel)
        self.adapter = kwargs.get('adapter', self.adapter)
        self.stealthlvl = kwargs.get('stealthlvl', self.stealthlvl)
        self.disclaimer = kwargs.get('disclaimer')
        self.help = kwargs.get('help')
        self.appendelements(kwargs.get('sets'))
        self.appendelements(kwargs.get('input'))
        self.appendelements(kwargs.get('output'))
        self.appendelements(kwargs.get('properties'))

    def appendelement(self, other):
        if isinstance(other, Set):
            self.sets += other
        elif isinstance(other, TransformProperty):
            self.properties += other
        elif isinstance(other, InputConstraint) or isinstance(other, InputEntity):
            self.input += other
        elif isinstance(other, OutputEntity):
            self.output += other

    def removeelement(self, other):
        if isinstance(other, Set):
            self.sets -= other
        if isinstance(other, TransformProperty):
            self.properties -= other
        elif isinstance(other, InputConstraint) or isinstance(other, InputEntity):
            self.input -= other
        elif isinstance(other, OutputEntity):
            self.output -= other


class BuiltInTransformSets(object):
    ConvertToDomain = "Convert to Domain"
    DomainsUsingMXNS = "Domains using MX NS"
    FindOnWebpage = "Find on webpage"
    RelatedEmailAddresses = "Related Email addresses"
    DNSFromDomain = "DNS from Domain"
    EmailAddressesFromDomain = "Email addresses from Domain"
    IPOwnerDetail = "IP owner detail"
    ResolveToIP = "Resolve to IP"
    DNSFromIP = "DNS from IP"
    EmailAddressesFromPerson = "Email addresses from Person"
    InfoFromNS = "Info from NS"
    DomainFromDNS = "Domain From DNS"
    FilesAndDocumentsFromDomain = "Files and Documents from Domain"
    LinksInAndOutOfSite = "Links in and out of site"
    DomainOwnerDetail = "Domain owner detail"
    FilesAndDocumentsFromPhrase = "Files and Documents from Phrase"


@XMLAttribute(name='name')
class Set(MaltegoElement):

    def __init__(self, name):
        super(Set, self).__init__(self.__class__.__name__)
        self.name = name


@XMLAttribute(name='name')
@XMLAttribute(name='description', default='')
@XMLSubElement(name='Transforms', propname='transforms', type=XSSubElementType.List)
class TransformSet(MaltegoElement):

    def __init__(self, name, **kwargs):
        super(TransformSet, self).__init__(self.__class__.__name__)
        self.name = name
        self.description = kwargs.get('description', self.description)
        self.appendelements(kwargs.get('transforms'))

    def appendelement(self, other):
        if isinstance(other, Transform):
            self.transforms += other

    def removeelement(self, other):
        if isinstance(other, Transform):
            self.transforms -= other


@XMLAttribute(name='max', type=XSAttributeType.Integer, default=1)
@XMLAttribute(name='min', type=XSAttributeType.Integer, default=1)
@XMLAttribute(name='type')
class InputConstraint(MaltegoElement):

    def __init__(self, type_, **kwargs):
        super(InputConstraint, self).__init__('Entity')
        self.type = type_
        self.min = kwargs.get('min', self.min)
        self.max = kwargs.get('max', self.max)


class OutputEntity(InputConstraint):
    pass


class InputEntity(InputConstraint):
    pass


class PropertyType(object):
    String = 'string'
    Boolean = 'boolean'
    Integer = 'int'


@XMLSubElement(name='DefaultValue', propname='defaultvalue')
@XMLSubElement(name='SampleValue', propname='samplevalue', default='')
@XMLAttribute(name='abstract', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='description', default='')
@XMLAttribute(name='displayName', propname='displayname')
@XMLAttribute(name='hidden', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='name')
@XMLAttribute(name='nullable', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='readonly', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='popup', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='type', default=PropertyType.String)
@XMLAttribute(name='visibility', default='public')
class TransformProperty(MaltegoElement):

    def __init__(self, name, default, displayname, description, **kwargs):
        super(TransformProperty, self).__init__("Property")
        self.name = name
        self.displayname = displayname
        self.defaultvalue = default
        self.description = description
        self.abstract = kwargs.get('abstract', self.abstract)
        self.samplevalue = kwargs.get('sample', self.samplevalue)
        self.hidden = kwargs.get('hidden', self.hidden)
        self.nullable = kwargs.get('nullable', self.nullable)
        self.popup = kwargs.get('popup', self.popup)
        self.readonly = kwargs.get('readonly', self.readonly)
        self.type = kwargs.get('type', self.type)
        self.visibility = kwargs.get('visibility', self.visibility)


@XMLAttribute(name='name')
@XMLAttribute(name='popup', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='type', default=PropertyType.String)
class TransformPropertySetting(MaltegoElement):

    def __init__(self, name, value, **kwargs):
        super(TransformPropertySetting, self).__init__("Property")
        self.name = name
        self.text = value
        self.popup = kwargs.get('popup', self.popup)
        self.type = kwargs.get('type', self.type)


def CmdLineTransformProperty(cmd=''):
    return TransformProperty(
        'transform.local.command',
        cmd,
        'Command line',
        'The command to execute for this transform'
    )


def CmdLineTransformPropertySetting(cmd=''):
    return TransformPropertySetting(
        'transform.local.command',
        cmd
    )


def CmdParmTransformProperty(params=''):
    return TransformProperty(
        'transform.local.parameters',
        params,
        'Command parameters',
        'The parameters to pass to the transform command'
    )


def CmdParmTransformPropertySetting(params=''):
    return TransformPropertySetting(
        'transform.local.parameters',
        params
    )


def CmdCwdTransformProperty(cwd=''):
    return TransformProperty(
        'transform.local.working-directory',
        cwd,
        'Working directory',
        'The working directory used when invoking the executable',
        sample_val='/'
    )


def CmdCwdTransformPropertySetting(cwd=''):
    return TransformPropertySetting(
        'transform.local.working-directory',
        cwd
    )


def CmdDbgTransformProperty(dbg=False):
    return TransformProperty(
        'transform.local.debug',
        str(dbg).lower(),
        'Show debug info',
        "When this is set, the transform's text output will be printed to the output window",
        sample_val=False,
        type=PropertyType.Boolean
    )


def CmdDbgTransformPropertySetting(dbg=False):
    return TransformPropertySetting(
        'transform.local.debug',
        str(dbg).lower(),
        type=PropertyType.Boolean
    )


@XMLAttribute(name='enabled', type=XSAttributeType.Bool, default=True)
@XMLAttribute(name='disclaimerAccepted', propname='accepted', type=XSAttributeType.Bool, default=False)
@XMLAttribute(name='showHelp', propname='show', type=XSAttributeType.Bool, default=True)
@XMLSubElement(name='Properties', propname='properties', type=XSSubElementType.List)
class TransformSettings(MaltegoElement):

    def __init__(self, **kwargs):
        super(TransformSettings, self).__init__(self.__class__.__name__)
        self.enabled = kwargs.get('enabled', self.enabled)
        self.accepted = kwargs.get('accepted', self.accepted)
        self.show = kwargs.get('show', self.show)
        self.appendelements(kwargs.get('properties'))

    def appendelement(self, other):
        if isinstance(other, TransformPropertySetting):
            self.properties += other

    def removeelement(self, other):
        if isinstance(other, TransformPropertySetting):
            self.properties -= other



@XMLAttribute(name='version', default=0.0, type=XSAttributeType.Float)
class Protocol(MaltegoElement):

    def __init__(self, **kwargs):
        super(Protocol, self).__init__(self.__class__.__name__)
        self.version = kwargs.get('version', self.version)


@XMLAttribute(name='type', default='none')
class Authentication(MaltegoElement):

    def __init__(self, **kwargs):
        super(Authentication, self).__init__(self.__class__.__name__)
        self.type = kwargs.get('type', self.type)


@XMLAttribute(name='name')
class Transform(MaltegoElement):

    def __init__(self, name):
        super(Transform, self).__init__(self.__class__.__name__)
        self.name = name


@XMLAttribute(name='name', default='Local')
@XMLAttribute(name='enabled', type=XSAttributeType.Bool, default=True)
@XMLAttribute(name='description', default='Local transforms hosted on this machine')
@XMLAttribute(name='url', default='http://localhost')
@XMLSubElement(name='LastSync', propname='lastsync', default=time.strftime('%Y-%m-%d %X.000 %Z'))
@XMLSubElement(name='Transforms', propname='transforms', type=XSSubElementType.List)
class MaltegoServer(MaltegoElement):

    def __init__(self, **kwargs):
        super(MaltegoServer, self).__init__(self.__class__.__name__)
        self.name = kwargs.get('name', self.name)
        self.enabled = kwargs.get('enabled', self.enabled)
        self.description = kwargs.get('description', self.description)
        self.url = kwargs.get('url', self.url)
        self.lastsync = kwargs.get('lastsync', self.lastsync)
        self.appendelements(kwargs.get('protocol'))
        self.appendelements(kwargs.get('authentication'))
        self.appendelements(kwargs.get('transforms'))

    def appendelement(self, other):
        if isinstance(other, Transform):
            self.transforms += other
        elif isinstance(other, Protocol) or isinstance(other, Authentication):
            self.append(other)

    def removeelement(self, other):
        if isinstance(other, Transform):
            self.transforms -= other
        elif isinstance(other, Protocol) or isinstance(other, Authentication):
            self.remove(other)


