#!/usr/bin/env python

from safedexml import Model, fields

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'MaltegoElement',
    'fields'
]


class MaltegoElement(Model):

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

    def appendelement(self, other):
        pass

    def removeelement(self, other):
        pass

    def __eq__(self, other):
        return self.render() == other.render()
