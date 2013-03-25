#!/usr/bin/env python

from message import Entity, EntityField, EntityFieldType

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'Affiliation',
    'AffiliationBebo',
    'AffiliationFacebook',
    'AffiliationFlickr',
    'AffiliationLinkedin',
    'AffiliationMySpace',
    'AffiliationOrkut',
    'AffiliationSpock',
    'AffiliationTwitter',
    'AffiliationWikiEdit',
    'AffiliationZoominfo',
    'Alias',
    'AS',
    'Banner',
    'BuiltWithTechnology',
    'Device',
    'DNSName',
    'Document',
    'Domain',
    'EmailAddress',
    'FacebookObject',
    'File',
    'GPS',
    'Image',
    'IPv4Address',
    'Location',
    'MXRecord',
    'Netblock',
    'NominatimLocation',
    'NSRecord',
    'Person',
    'PhoneNumber',
    'Phrase',
    'Port',
    'Service',
    'Twit',
    'URL',
    'Vuln',
    'Webdir',
    'Website',
    'WebTitle'
]


@EntityField(name='properties.gps', displayname='GPS Co-ordinate')
@EntityField(name='latitude', displayname='Latitude', type=EntityFieldType.Float)
@EntityField(name='longitude', displayname='Longitude', type=EntityFieldType.Float)
class GPS(Entity):
    pass


@EntityField(name='properties.device', displayname='Device')
class Device(Entity):
    pass


@EntityField(name='properties.builtwithtechnology', propname='builtwith', displayname='BuiltWith Technology')
class BuiltWithTechnology(Entity):
    pass



@EntityField(name='fqdn', displayname='Domain Name')
@EntityField(name='whois', displayname='WHOIS Info')
class Domain(Entity):
    pass


@EntityField(name='fqdn', displayname='DNS Name')
class DNSName(Entity):
    pass


@EntityField(name='fqdn', displayname='MX Record')
@EntityField(name='mxrecord.priority', propname='mxpriority', type=EntityFieldType.Integer)
class MXRecord(Entity):
    pass


@EntityField(name='fqdn', displayname='NS Record')
class NSRecord(Entity):
    pass


@EntityField(name='ipv4-address', propname='ipv4address', displayname='IP Address')
@EntityField(name='ipaddress.internal', propname='internal', displayname='Internal', type=EntityFieldType.Bool)
class IPv4Address(Entity):
    pass


@EntityField(name='ipv4-range', propname='ipv4range', displayname='IP Range')
class Netblock(Entity):
    pass


@EntityField(name='as.number', propname='number', displayname='AS Number', type=EntityFieldType.Integer)
class AS(Entity):
    pass


@EntityField(name='website.ssl-enabled', displayname='SSL Enabled', type=EntityFieldType.Bool)
@EntityField(name='fqdn', displayname='Website')
@EntityField(name='ports', displayname='Ports', type=EntityFieldType.Integer)
class Website(Entity):
    pass


@EntityField(name='maltego.v2.value.property', propname='shorttitle', displayname='Short title')
@EntityField(name='theurl', propname='url', displayname='URL')
@EntityField(name='fulltitle', displayname='Title')
class URL(Entity):
    pass


@EntityField(name='text', displayname='Text')
class Phrase(Entity):
    pass


@EntityField(name='maltego.v2.value.property', propname='title', displayname='Title')
@EntityField(name='link', propname='url', displayname='URL')
@EntityField(name='metainfo', propname='metadata', displayname='Meta-Data')
class Document(Entity):
    pass


@EntityField(name='lastname', propname='lastname', displayname='Surname')
@EntityField(name='firstname', propname='firstnames', displayname='First Names')
@EntityField(name='person.fullname', propname='fullname', displayname='Full Name')
class Person(Entity):
    pass


@EntityField(name='email', displayname='Email Address')
class EmailAddress(Entity):
    pass


@EntityField(name='content', displayname='Content')
@EntityField(name='pubdate', displayname='Date published')
@EntityField(name='imglink', displayname='Image Link')
@EntityField(name='author', displayname='Author')
@EntityField(name='title', displayname='Title')
@EntityField(name='author_uri', propname='authoruri', displayname='Author URI')
@EntityField(name='twit.name', propname='twitname', displayname='Twit')
@EntityField(name='id', displayname='Twit ID')
class Twit(Entity):
    pass


@EntityField(name='person.name', propname='name', displayname='Name')
@EntityField(name='uid', displayname='UID')
@EntityField(name='network', displayname='Network')
@EntityField(name='profile_url', propname='profileurl', displayname='Profile URL')
class Affiliation(Entity):
    pass


class AffiliationBebo(Affiliation):
    pass


class AffiliationFacebook(Affiliation):
    name = "affiliation.Facebook"


class AffiliationFlickr(Affiliation):
    name = "affiliation.Flickr"


class AffiliationLinkedin(Affiliation):
    pass


class AffiliationMySpace(Affiliation):
    pass


class AffiliationOrkut(Affiliation):
    pass


class AffiliationSpock(Affiliation):
    pass


@EntityField(name='properties.facebookobject', propname='object', displayname='Facebook Object')
class FacebookObject(Entity):
    pass


@EntityField(name='twitter.number', propname='number', displayname='Twitter Number', type=EntityFieldType.Integer)
@EntityField(name='twitter.screen-name', propname='screenname', displayname='Screen Name')
@EntityField(name='twitter.friendcount', propname='friendcount', displayname='Friend Count', type=EntityFieldType.Integer)
@EntityField(name='person.fullname', propname='fullname', displayname='Real Name')
class AffiliationTwitter(Affiliation):
    name = "affiliation.Twitter"


class AffiliationZoominfo(Affiliation):
    pass


class AffiliationWikiEdit(Affiliation):
    pass


@EntityField(name='city', displayname='City')
@EntityField(name='countrysc', propname='countrycode', displayname='Country Code')
@EntityField(name='area', displayname='Area')
@EntityField(name='country', displayname='Country')
@EntityField(name='long', propname='longitude', displayname='Longitude', type=EntityFieldType.Float)
@EntityField(name='lat', propname='latitude', displayname='Latitude', type=EntityFieldType.Float)
@EntityField(name='streetaddress', displayname='Street Address')
@EntityField(name='location.areacode', displayname='Area Code')
@EntityField(name='location.name', propname='locationname', displayname='Name')
class Location(Entity):
    pass


@EntityField(name='properties.nominatimlocation', propname='nominatim', displayname='Nominatim Location')
class NominatimLocation(Entity):
    pass


@EntityField(name='areacode', displayname='Area Code')
@EntityField(name='lastnumbers', displayname='Last Digits')
@EntityField(name='citycode', displayname='City Code')
@EntityField(name='phonenumber', displayname='Phone Number')
@EntityField(name='countrycode', displayname='Country Code')
class PhoneNumber(Entity):
    pass


@EntityField(name='properties.alias', propname='alias', displayname='Alias')
class Alias(Entity):
    pass


@EntityField(name='properties.image', propname='description', displayname='Description')
@EntityField(name='fullImage', propname='url', displayname='URL')
class Image(Entity):
    pass


@EntityField(name='source', displayname='Source')
@EntityField(name='description', displayname='Description')
class File(Entity):
    pass


class Banner(Entity):
    pass


class Port(Entity):
    pass


class Service(Entity):
    pass


class Vuln(Entity):
    pass


class Webdir(Entity):
    pass


@EntityField(name='title', displayname='Title')
class WebTitle(Entity):
    pass