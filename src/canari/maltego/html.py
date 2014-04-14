# !/usr/bin/env python

from xml.etree.ElementTree import Element, tostring


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'HTML',
    'TABLE',
    'TR',
    'TD',
    'A',
    'IMG',
    'Table'
]


class HTML(Element):
    def __init__(self, tag='html', attrib={}, **extra):
        attrib = attrib.copy()
        attrib.update(extra)
        super(HTML, self).__init__(tag, attrib)

    def __add__(self, other):
        self.append(other)
        return self

    __iadd__ = __add__

    def __sub__(self, other):
        self.remove(other)
        return self

    __isub__ = __sub__

    def __str__(self):
        return tostring(self)


class TABLE(HTML):
    def __init__(self, title="GENERAL INFORMATION", colspan="2", **kwargs):
        super(TABLE, self).__init__(
            "table",
            attrib={
                'width': '100%',
                'border': '1',
                'rules': 'cols',
                'frame': 'box',
                'cellpadding': '2'
            }
        )

        tr = TR()
        self.append(tr)
        tr.append(TD(title, colspan=colspan, css_class=TD.ONE))

        for i in kwargs:
            self.set(i, str(kwargs[i]) if not isinstance(kwargs[i], basestring) else kwargs[i])


class TR(HTML):
    def __init__(self):
        super(TR, self).__init__('tr')


class A(HTML):
    def __init__(self, label, href, **kwargs):
        attrib = {'href': href}
        attrib.update(kwargs)
        super(A, self).__init__(
            'a',
            attrib=attrib
        )
        self.text = label


class IMG(HTML):
    def __init__(self, src, **kwargs):
        attrib = {'src': src}
        attrib.update(kwargs)

        super(IMG, self).__init__(
            'img',
            attrib=attrib
        )


class TD(HTML):
    ONE = "one"
    TWO = "two"
    THREE = "three"
    VALUE = "value"

    def __init__(self, value, css_class=TWO, align="center", **kwargs):
        super(TD, self).__init__(
            'td',
            attrib={
                'class': css_class,
                'align': align,
            }
        )
        self.text = str(value) if not isinstance(value, basestring) else value

        for i in kwargs:
            self.set(i, str(kwargs[i]) if not isinstance(kwargs[i], basestring) else kwargs[i])


class Table(object):
    def __init__(self, columns, title='GENERAL INFORMATION'):
        self._rows = []
        self._title = title
        self._rows.append([TD(c, TD.THREE) for c in columns])

    def addrow(self, columns):
        self._rows.append([TD(c) for c in columns])

    def __str__(self):
        self.table = TABLE(self._title, colspan=len(self._rows[0]))
        for r in self._rows:
            tr = TR()
            c = tr.getchildren()
            c += r
            self.table += tr
        return str(self.table)
