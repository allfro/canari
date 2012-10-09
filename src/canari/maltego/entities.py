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
    'Device',
    'BuiltWithTechnology',
    'Domain',
    'DNSName',
    'MXRecord',
    'NSRecord',
    'IPv4Address',
    'Netblock',
    'AS',
    'Website',
    'URL',
    'Phrase',
    'Document',
    'Person',
    'EmailAddress',
    'Twit',
    'Affiliation',
    'AffiliationBebo',
    'AffiliationFacebook',
    'AffiliationFlickr',
    'AffiliationLinkedin',
    'AffiliationMySpace',
    'AffiliationOrkut',
    'AffiliationSpock',
    'AffiliationTwitter',
    'AffiliationZoominfo',
    'AffiliationWikiEdit',
    'Location',
    'PhoneNumber',
    'Banner',
    'Port',
    'Service',
    'Vuln',
    'Webdir',
    'WebTitle'
]


class Device(Entity):
    pass


class BuiltWithTechnology(Entity):
    pass


@EntityField(name='fqdn', displayname='Domain Name')
@EntityField(name='whois-info', propname='whoisinfo', displayname='WHOIS Info')
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


@EntityField(name='http', displayname='HTTP Ports')
@EntityField(name='https', displayname='HTTPS Ports')
@EntityField(name='servertype', displayname='Server Banner')
@EntityField(name='URLS', propname='urls', displayname='URLs')
class Website(Entity):
    pass


@EntityField(name='fqdn', displayname='Website')
@EntityField(name='website.ssl-enabled', propname='ssl', displayname='SSL Enabled', type=EntityFieldType.Bool)
@EntityField(name='ports', displayname='Ports')
class URL(Entity):
    pass


@EntityField(name='text', displayname='Text')
class Phrase(Entity):
    pass


@EntityField(name='title', displayname='Title')
@EntityField(name='document.meta-data', propname='metadata', displayname='Meta-Data')
@EntityField(name='url', displayname='URL')
class Document(Entity):
    pass


@EntityField(name='person.fullname', propname='fullname', displayname='Full Name')
@EntityField(name='person.firstnames', propname='firstnames', displayname='First Names')
@EntityField(name='person.lastname', propname='lastname', displayname='Surname')
class Person(Entity):
    pass


@EntityField(name='email', displayname='Email Address')
class EmailAddress(Entity):
    pass


@EntityField(name='twit.name', propname='name', displayname='Twit')
@EntityField(name='id', displayname='Twit ID')
@EntityField(name='author', displayname='Author')
@EntityField(name='author_uri', propname='authoruri', displayname='AUthor URI')
@EntityField(name='content', displayname='Content')
@EntityField(name='imglink', displayname='Image Link')
@EntityField(name='pubdate', displayname='Date published')
@EntityField(name='title', displayname='Title')
class Twit(Entity):
    pass


@EntityField(name='person.name', propname='name', displayname='Name')
@EntityField(name='affiliation.uid', propname='uid', displayname='UID')
@EntityField(name='affiliation.network', propname='network', displayname='Network')
@EntityField(name='affiliation.profile-url', propname='profileurl', displayname='Profile URL')
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


@EntityField(name='twitter.number', propname='number', displayname='Twitter Number')
@EntityField(name='twitter.screen-name', propname='number', displayname='Screen Name')
@EntityField(name='twitter.friendcount', propname='number', displayname='Friend Count')
@EntityField(name='twitter.fullname', propname='fullname', displayname='Real Name')
class AffiliationTwitter(Affiliation):
    name = "affiliation.Twitter"


class AffiliationZoominfo(Affiliation):
    pass


class AffiliationWikiEdit(Affiliation):
    pass


@EntityField(name='location.name', propname='name', displayname='Name')
@EntityField(name='country', displayname='Country')
@EntityField(name='city', displayname='City')
@EntityField(name='location.area', propname='area', displayname='Area')
@EntityField(name='countrycode', displayname='Country Code')
@EntityField(name='longitude', displayname='Longitude')
@EntityField(name='latitude', displayname='Latitude')
class Location(Entity):
    pass


@EntityField(name='phonenumber', displayname='Phone Number')
@EntityField(name='phonenumber.countrycode', propname='countrycode', displayname='Country Code')
@EntityField(name='phonenumber.citycode', propname='citycode', displayname='City Code')
@EntityField(name='phonenumber.areacode', propname='areacode', displayname='Area Code')
@EntityField(name='phonenumber.lastnumbers', propname='lastnumbers', displayname='Last Digits')
class PhoneNumber(Entity):
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