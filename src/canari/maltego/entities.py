#!/usr/bin/env python

from message import Entity, EntityField, EntityFieldType

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'Affiliation',
    'Bebo',
    'Facebook',
    'Flickr',
    'Linkedin',
    'MySpace',
    'Orkut',
    'Spock',
    'Twitter',
    'WikiEdit',
    'Zoominfo',
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
    'Vulnerability',
    'Webdir',
    'Website',
    'WebTitle'
]


class Unknown(Entity):
    pass


@EntityField(name='properties.gps', propname='gps', displayname='GPS Co-ordinate', is_value=True)
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



@EntityField(name='fqdn', displayname='Domain Name', is_value=True)
@EntityField(name='whois-info', propname='whois_info', displayname='WHOIS Info')
class Domain(Entity):
    _v2type_ = 'Domain'
    _fields_to_properties_ = {
        'whois': 'whois_info'
    }


@EntityField(name='fqdn', displayname='DNS Name', is_value=True)
class DNSName(Entity):
    _v2type_ = 'DNSName'


@EntityField(name='mxrecord.priority', propname='priority', type=EntityFieldType.Integer)
class MXRecord(DNSName):
    _v2type_ = 'MXRecord'


class NSRecord(DNSName):
    _v2type_ = 'NSRecord'


@EntityField(name='ipv4-address', propname='ipv4address', displayname='IP Address', is_value=True)
@EntityField(name='ipaddress.internal', propname='internal', displayname='Internal', type=EntityFieldType.Bool)
class IPv4Address(Entity):
    _v2type_ = 'IPAddress'


@EntityField(name='ipv4-range', propname='ipv4range', displayname='IP Range', is_value=True)
class Netblock(Entity):
    _v2type_ = 'Netblock'


@EntityField(name='as.number', propname='number', displayname='AS Number', type=EntityFieldType.Integer, is_value=True)
class AS(Entity):
    _v2type_ = 'ASNumber'


@EntityField(name='website.ssl-enabled', propname='ssl_enabled', displayname='SSL Enabled', type=EntityFieldType.Bool)
@EntityField(name='fqdn', displayname='Website', is_value=True)
@EntityField(name='ports', displayname='Ports', type=EntityFieldType.Integer)
class Website(Entity):
    _v2type_ = 'Website'


@EntityField(name='short-title', propname='short_title', displayname='Short title', is_value=True)
@EntityField(name='url', displayname='URL')
@EntityField(name='title', displayname='Title')
class URL(Entity):
    _v2type_ = 'URL'
    _fields_to_properties_ = {
        'maltego.v2.value.property': 'shorttitle',
        'theurl': 'url',
        'fulltitle': 'title'
    }


@EntityField(name='text', displayname='Text', is_value=True)
class Phrase(Entity):
    _v2type_ = 'Phrase'


@EntityField(name='title', displayname='Title')
@EntityField(name='url', displayname='URL', is_value=True)
@EntityField(name='document.metadata', propname='metadata', displayname='Meta-Data')
class Document(Entity):
    _v2type_ = 'Document'
    _fields_to_properties_ = {
        'maltego.v2.value.property': 'title',
        'link': 'url',
        'metainfo': 'metadata'
    }


@EntityField(name='person.lastname', propname='lastname', displayname='Surname')
@EntityField(name='person.firstnames', propname='firstnames', displayname='First Names')
@EntityField(name='person.fullname', propname='fullname', displayname='Full Name', is_value=True)
class Person(Entity):
    _v2type_ = 'Person'
    _fields_to_properties_ = {
        'lastname': 'lastname',
        'firstname': 'firstnames'
    }


@EntityField(name='email', displayname='Email Address', is_value=True)
class EmailAddress(Entity):
    _v2type_ = 'EmailAddress'


@EntityField(name='content', displayname='Content')
@EntityField(name='pubdate', displayname='Date published')
@EntityField(name='img_link', displayname='Image Link')
@EntityField(name='author', displayname='Author')
@EntityField(name='title', displayname='Title')
@EntityField(name='author_uri', displayname='Author URI')
@EntityField(name='twit.name', propname='name', displayname='Twit', is_value=True)
@EntityField(name='id', displayname='Twit ID')
class Twit(Entity):
    _v2type_ = 'Twit'
    _fields_to_properties_ = {
        'imglink': 'img_link'
    }


@EntityField(name='person.name', propname='person_name', displayname='Name', is_value=True)
@EntityField(name='affiliation.uid', propname='uid', displayname='UID')
@EntityField(name='affiliation.network', propname='network', displayname='Network')
@EntityField(name='affiliation.profile-url', propname='profile_url', displayname='Profile URL')
class Affiliation(Entity):
    _namespace_ = 'maltego.affiliation'
    _fields_to_properties_ = {
        'network': 'network',
        'uid': 'uid',
        'profile_url': 'profile_url'
    }


class Bebo(Affiliation):
    _v2type_ = 'AffiliationBebo'


class Facebook(Affiliation):
    _v2type_ = 'AffiliationFacebook'


class Flickr(Affiliation):
    _v2type_ = 'AffiliationFlickr'


class Linkedin(Affiliation):
    _v2type_ = 'AffiliationLinkedin'


class MySpace(Affiliation):
    _v2type_ = 'AffiliationMySpace'


class Orkut(Affiliation):
    _v2type_ = 'AffiliationOrkut'


@EntityField(name='twitter.number', propname='number', displayname='Twitter Number', type=EntityFieldType.Integer)
@EntityField(name='twitter.screen-name', propname='screenname', displayname='Screen Name')
@EntityField(name='twitter.friendcount', propname='friendcount', displayname='Friend Count',
             type=EntityFieldType.Integer)
@EntityField(name='person.fullname', propname='fullname', displayname='Real Name')
class Twitter(Affiliation):
    _v2type_ = 'AffiliationTwitter'


class Zoominfo(Affiliation):
    pass


class WikiEdit(Affiliation):
    pass


@EntityField(name='spock.websites', propname='websites', displayname='Listed Websites')
class Spock(Affiliation):
    _v2type_ = 'AffiliationSpock'


@EntityField(name='properties.facebookobject', propname='object', displayname='Facebook Object')
class FacebookObject(Entity):
    pass


@EntityField(name='city', displayname='City')
@EntityField(name='countrycode', displayname='Country Code')
@EntityField(name='location.area', propname='area', displayname='Area')
@EntityField(name='country', displayname='Country')
@EntityField(name='longitude', displayname='Longitude', type=EntityFieldType.Float)
@EntityField(name='latitude', displayname='Latitude', type=EntityFieldType.Float)
@EntityField(name='streetaddress', displayname='Street Address')
@EntityField(name='location.areacode', propname='areacode', displayname='Area Code')
@EntityField(name='location.name', propname='name', displayname='Name', is_value=True)
class Location(Entity):
    _v2type_ = 'Location'
    _fields_to_properties_ = {
        'countrysc': 'countrycode',
        'area': 'area',
        'long': 'longitude',
        'lat': 'latitude'
    }


@EntityField(name='properties.nominatimlocation', propname='nominatim', displayname='Nominatim Location', is_value=True)
class NominatimLocation(Entity):
    pass


@EntityField(name='phonenumber.areacode', propname='areacode', displayname='Area Code')
@EntityField(name='phonenumber.lastnumbers', propname='lastnumbers', displayname='Last Digits')
@EntityField(name='phonenumber.citycode', propname='citycode', displayname='City Code')
@EntityField(name='phonenumber', displayname='Phone Number', is_value=True)
@EntityField(name='phonenumber.countrycode', propname='countrycode', displayname='Country Code')
class PhoneNumber(Entity):
    _v2type_ = 'PhoneNumber'
    _fields_to_properties_ = {
        'countrycode': 'countrycode',
        'citycode': 'citycode',
        'areacode': 'areacode',
        'lastnumbers': 'lastnumbers'
    }


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


@EntityField(name='banner.text', propname='text', displayname='Banner', is_value=True)
class Banner(Entity):
    _v2type_ = 'Banner'


@EntityField(name='port.number', propname='number', displayname='Ports', is_value=True)
class Port(Entity):
    _v2type_ = 'Port'


@EntityField(name='service.name', propname='name', displayname='Description', is_value=True)
@EntityField(name='banner.text', propname='banner', displayname='Service Banner')
@EntityField(name='port.number', propname='port', displayname='Ports')
class Service(Entity):
    _v2type_ = 'Service'


@EntityField(name='vulnerability.id', propname='id', displayname='ID', is_value=True)
class Vulnerability(Entity):
    _v2type_ = 'Vuln'


@EntityField(name='directory.name', propname='name', displayname='Name', is_value=True)
class Webdir(Entity):
    _v2type_ = 'Webdir'


@EntityField(name='title', displayname='Title', is_value=True)
class WebTitle(Entity):
    _v2type_ = 'WebTitle'