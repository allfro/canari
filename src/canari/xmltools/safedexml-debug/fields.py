"""

dexml.fields:  basic field type definitions for dexml
=====================================================

"""

import safedexml as dexml
import random
from xml.sax.saxutils import escape, quoteattr



class _AttrBucket(object):
    """A simple class used only to hold attributes."""
    pass


class Field(object):
    """Base class for all dexml Field classes.

    Field classes are responsible for parsing and rendering individual
    components to the XML.  They also act as descriptors on dexml Model
    instances, to get/set the corresponding properties.

    Each field instance will magically be given the following properties:

      * model_class:  the Model subclass to which it is attached
      * field_name:   the name under which is appears on that class

    The following methods are required for interaction with the parsing
    and rendering machinery:

      * parse_attributes:    parse info out of XML node attributes
      * parse_child_node:    parse into out of an XML child node
      * render_attributes:   render XML for node attributes
      * render_children:     render XML for child nodes
      
    """

    #  Global counter tracking the order in which fields are declared.
    _order_counters_ = 0


    class arguments:
        required = True

    def __init__(self, **kwds):
        """Default Field constructor.

        This constructor keeps track of the order in which Field instances
        are created, since this information can have semantic meaning in
        XML.  It also merges any keyword arguments with the defaults
        defined on the 'arguments' inner class, and assigned these attributes
        to the Field instance.
        """
        self._order_counter = Field._order_counters_ = Field._order_counters_ + 1
        args = self.__class__.arguments
        for argnm in dir(args):
            if not argnm.startswith("__"):
                setattr(self, argnm, kwds.get(argnm, getattr(args, argnm)))

    def parse_attributes(self, obj, attrs):
        """Parse any attributes for this field from the given list.

        This method will be called with the Model instance being parsed and
        a list of attribute nodes from its XML tag.  Any attributes of 
        interest to this field should be processed, and a list of the unused
        attribute nodes returned.
        """
        return attrs

    def parse_child_node(self, obj, node):
        """Parse a child node for this field.

        This method will be called with the Model instance being parsed and
        the current child node of that model's XML tag.  There are three
        options for processing this node:

            * return PARSE_DONE, indicating that it was consumed and this
              field now has all the necessary data.
            * return PARSE_MORE, indicating that it was consumed but this
              field will accept more nodes.
            * return PARSE_SKIP, indicating that it was not consumed by
              this field.

        Any other return value will be taken as a parse error.
        """
        print "parse_child_node called on the base 'Field' class"
        return dexml.PARSE_SKIP

    def parse_done(self, obj):
        """Finalize parsing for the given object.

        This method is called as a simple indicator that no more data will
        be forthcoming.  No return value is expected.
        """
        pass

    def render_attributes(self, obj, val, nsmap):
        """Render any attributes that this field manages."""
        return []

    def render_children(self, obj, nsmap, val):
        """Render any child nodes that this field manages."""
        return []

    def __get__(self, instance, owner=None):
        print 'Field.__get__:', 'self:', self, 'instance:', instance, 'owner:', owner
        if instance is None:
            print '\t instance was None, returning self'
            return self
        
        print '\t getting return value'
        res = instance.__dict__.get(self.field_name)
        print '\t instance __dict__:', instance.__dict__
        print '\t returning:', res, 'from field name:', self.field_name
        return res

    def __set__(self, instance, value):
        print 'Field.__set__', self, instance, self.field_name, '<-', value
        print '\t Instance dict (before):', instance.__dict__
        instance.__dict__[self.field_name] = value
        print '\t Instance dict (after):', instance.__dict__


    def _check_tagname(self, node, tagname):
        if node.nodeType != node.ELEMENT_NODE:
            return False
        if isinstance(tagname, basestring):
            if node.localName != tagname:
                return False
            if node.namespaceURI:
                if node.namespaceURI != self.model_class.meta.namespace:
                    return False
        else:
            (tagns, tagname) = tagname
            if node.localName != tagname:
                return False
            if node.namespaceURI != tagns:
                return False
        return True


class Value(Field):
    """Field subclass that holds a simple scalar value.

    This Field subclass contains the common logic to parse/render simple
    scalar value fields - fields that don't required any recursive parsing.
    Individual subclasses should provide the parse_value() and render_value()
    methods to do type coercion of the value.

    Value fields can also have a default value, specified by the 'default'
    keyword argument.

    By default, the field maps to an attribute of the model's XML node with
    the same name as the field declaration.  Consider:

        class MyModel(Model):
            my_field = fields.Value(default="test")


    This corresponds to the XML fragment "<MyModel my_field='test' />".
    To use a different name specify the 'attrname' kwd argument.  To use
    a subtag instead of an attribute specify the 'tagname' kwd argument.

    Namespaced attributes or subtags are also supported, by specifying a
    (namespace,tagname) pair for 'attrname' or 'tagname' respectively.
    """

    class arguments(Field.arguments):
        tagname = None
        attrname = None
        default = None

    def __init__(self, **kwds):
        super(Value, self).__init__(**kwds)
        if self.default is not None:
            self.required = False

    def _get_attrname(self):
        if self.__dict__["tagname"]:
            return None
        attrname = self.__dict__['attrname']
        if not attrname:
            attrname = self.field_name
        return attrname

    def _set_attrname(self, attrname):
        self.__dict__['attrname'] = attrname

    attrname = property(_get_attrname, _set_attrname)

    def _get_tagname(self):
        if self.__dict__["attrname"]:
            return None
        tagname = self.__dict__['tagname']
        if tagname and not isinstance(tagname, (basestring, tuple)):
            tagname = self.field_name
        return tagname

    def _set_tagname(self, tagname):
        self.__dict__['tagname'] = tagname

    tagname = property(_get_tagname, _set_tagname)

    def __get__(self, instance, owner=None):
        val = super(Value, self).__get__(instance, owner)
        if val is None:
            return self.default
        return val

    def parse_attributes(self, obj, attrs):
        #  Bail out if we're attached to a subtag rather than an attr.
        if self.tagname:
            return attrs
        unused = []
        attrname = self.attrname
        if isinstance(attrname, basestring):
            ns = None
        else:
            (ns, attrname) = attrname
        for attr in attrs:
            if attr.localName == attrname:
                if attr.namespaceURI == ns:
                    self.__set__(obj, self.parse_value(attr.nodeValue))
                else:
                    unused.append(attr)
            else:
                unused.append(attr)
        return unused

    def parse_child_node(self, obj, node):
        if not self.tagname:
            return dexml.PARSE_SKIP
        if self.tagname == ".":
            node = node.parentNode
        else:
            if not self._check_tagname(node, self.tagname):
                return dexml.PARSE_SKIP
        vals = []
        #  Merge all text nodes into a single value
        for child in node.childNodes:
            if child.nodeType not in (child.TEXT_NODE, child.CDATA_SECTION_NODE):
                raise dexml.ParseError("non-text value node")
            vals.append(child.nodeValue)
        self.__set__(obj, self.parse_value("".join(vals)))
        return dexml.PARSE_DONE

    def render_attributes(self, obj, val, nsmap):
        if val is not None and self.attrname:
            qaval = quoteattr(self.render_value(val))
            if isinstance(self.attrname, basestring):
                yield '%s=%s' % (self.attrname, qaval,)
            else:
                m_meta = self.model_class.meta
                (ns, nm) = self.attrname
                if ns == m_meta.namespace and m_meta.namespace_prefix:
                    prefix = m_meta.namespace_prefix
                    yield '%s:%s=%s' % (prefix, nm, qaval,)
                elif ns is None:
                    yield '%s=%s' % (nm, qaval,)
                else:
                    for (p, n) in nsmap.iteritems():
                        if ns == n[0]:
                            prefix = p
                            break
                    else:
                        prefix = "p" + str(random.randint(0, 10000))
                        while prefix in nsmap:
                            prefix = "p" + str(random.randint(0, 10000))
                        yield 'xmlns:%s="%s"' % (prefix, ns,)
                    yield '%s:%s=%s' % (prefix, nm, qaval,)

    def render_children(self, obj, val, nsmap):
        if val is not None and self.tagname:
            val = self._esc_render_value(val)
            if self.tagname == ".":
                yield val
            else:
                attrs = ""
                #  By default, tag values inherit the namespace of their
                #  containing model class.
                if isinstance(self.tagname, basestring):
                    prefix = self.model_class.meta.namespace_prefix
                    localName = self.tagname
                else:
                    m_meta = self.model_class.meta
                    (ns, localName) = self.tagname
                    if not ns:
                        #  If we have an explicitly un-namespaced tag,
                        #  we need to be careful.  The model tag might have
                        #  set the default namespace, which we need to undo.
                        prefix = None
                        if m_meta.namespace and not m_meta.namespace_prefix:
                            attrs = ' xmlns=""'
                    elif ns == m_meta.namespace:
                        prefix = m_meta.namespace_prefix
                    else:
                        for (p, n) in nsmap.iteritems():
                            if ns == n[0]:
                                prefix = p
                                break
                        else:
                            prefix = "p" + str(random.randint(0, 10000))
                            while prefix in nsmap:
                                prefix = "p" + str(random.randint(0, 10000))
                            attrs = ' xmlns:%s="%s"' % (prefix, ns)
                yield self._render_tag(val, prefix, localName, attrs)

    def _render_tag(self, val, prefix, localName, attrs):
        if val:
            if prefix:
                args = (prefix, localName, attrs, val, prefix, localName)
                return "<%s:%s%s>%s</%s:%s>" % args
            else:
                return "<%s%s>%s</%s>" % (localName, attrs, val, localName)
        else:
            if prefix:
                return "<%s:%s%s />" % (prefix, localName, attrs,)
            else:
                return "<%s%s />" % (localName, attrs)

    def parse_value(self, val):
        return val

    def render_value(self, val):
        if not isinstance(val, basestring):
            val = str(val)
        return val

    def _esc_render_value(self, val):
        return escape(self.render_value(val))


class String(Value):
    """Field representing a simple string value."""
    # actually, the base Value() class will do this automatically.
    pass


class CDATA(Value):
    """String field rendered as CDATA."""

    def __init__(self, **kwds):
        super(CDATA, self).__init__(**kwds)
        if self.__dict__.get("tagname", None) is None:
            raise ValueError("CDATA fields must have a tagname")

    def _esc_render_value(self, val):
        val = self.render_value(val)
        val = val.replace("]]>", "]]]]><![CDATA[>")
        return "<![CDATA[" + val + "]]>"


class Integer(Value):
    """Field representing a simple integer value."""

    def parse_value(self, val):
        return int(val)


class Float(Value):
    """Field representing a simple float value."""

    def parse_value(self, val):
        return float(val)


class Boolean(Value):
    """Field representing a simple boolean value.

    The strings corresponding to false are 'no', 'off', 'false' and '0',
    compared case-insensitively.  Note that this means an empty tag or
    attribute is considered True - this is usually what you want, since 
    a completely missing attribute or tag can be interpreted as False.

    To enforce that the presence of a tag indicates True and the absence of
    a tag indicates False, pass the keyword argument "empty_only".
    """

    class arguments(Value.arguments):
        empty_only = False

    def __init__(self, **kwds):
        super(Boolean, self).__init__(**kwds)
        if self.empty_only:
            self.required = False

    def __set__(self, instance, value):
        instance.__dict__[self.field_name] = bool(value)

    def parse_value(self, val):
        if self.empty_only and val != "":
            raise ValueError("non-empty value in empty_only Boolean")
        if val.lower() in ("no", "off", "false", "0"):
            return False
        return True

    def render_children(self, obj, val, nsmap):
        if not val and self.empty_only:
            return []
        return super(Boolean, self).render_children(obj, val, nsmap)

    def render_attributes(self, obj, val, nsmap):
        if not val and self.empty_only:
            return []
        return super(Boolean, self).render_attributes(obj, val, nsmap)

    def render_value(self, val):
        if not val:
            return "false"
        if self.empty_only:
            return ""
        return "true"


class Model(Field):
    """Field subclass referencing another Model instance.

    This field sublcass allows Models to contain other Models recursively.
    The first argument to the field constructor must be either a Model
    class, or the name or tagname of a Model class.
    """

    class arguments(Field.arguments):
        type = None

    def __init__(self, type=None, **kwds):
        kwds["type"] = type
        super(Model, self).__init__(**kwds)

    def _get_type(self):
        return self.__dict__.get("type")

    def _set_type(self, value):
        if value is not None:
            self.__dict__["type"] = value

    type = property(_get_type, _set_type)

    def __set__(self, instance, value):
        typeclass = self.typeclass
        if value and not isinstance(value, typeclass):
            raise ValueError("Invalid value type %s. Model field requires %s instance" %
                             (value.__class__.__name__, typeclass.__name__))
        super(Model, self).__set__(instance, value)

    @property
    def typeclass(self):
        try:
            return self.__dict__['typeclass']
        except KeyError:
            self.__dict__['typeclass'] = self._load_typeclass()
            return self.__dict__['typeclass']

    def _load_typeclass(self):
        typ = self.type
        if isinstance(typ, dexml.ModelMetaclass):
            return typ
        if typ is None:
            typ = self.field_name
        typeclass = None
        if isinstance(typ, basestring):
            if self.model_class.meta.namespace:
                ns = self.model_class.meta.namespace
                typeclass = dexml.ModelMetaclass.find_class(typ, ns)
            if typeclass is None:
                typeclass = dexml.ModelMetaclass.find_class(typ, None)
            if typeclass is None:
                raise ValueError("Unknown Model class: %s" % (typ,))
        else:
            (ns, typ) = typ
            if isinstance(typ, dexml.ModelMetaclass):
                return typ
            typeclass = dexml.ModelMetaclass.find_class(typ, ns)
            if typeclass is None:
                raise ValueError("Unknown Model class: (%s,%s)" % (ns, typ))
        return typeclass

    def parse_child_node(self, obj, node):
        typeclass = self.typeclass
        try:
            typeclass.validate_xml_node(node)
        except dexml.ParseError:
            return dexml.PARSE_SKIP
        else:
            inst = typeclass.parse(node)
            self.__set__(obj, inst)
            return dexml.PARSE_DONE

    def render_attributes(self, obj, val, nsmap):
        return []

    def render_children(self, obj, val, nsmap):
        if val is not None:
            for data in val._render(nsmap):
                yield data


class List(Field):
    """Field subclass representing a list of fields.

    This field corresponds to a homogenous list of other fields.  You would
    declare it like so:

      class MyModel(Model):
          items = fields.List(fields.String(tagname="item"))

    Corresponding to XML such as:

      <MyModel><item>one</item><item>two</item></MyModel>


    The properties 'minlength' and 'maxlength' control the allowable length
    of the list.

    The 'tagname' property sets an optional wrapper tag which acts as container
    for list items, for example:

      class MyModel(Model):
          items = fields.List(fields.String(tagname="item"),
                              tagname='list')

    Corresponding to XML such as:

      <MyModel><list><item>one</item><item>two</item></list></MyModel>

    This wrapper tag is always rendered, even if the list is empty.  It is
    transparently removed when parsing.
    """

    class arguments(Field.arguments):
        field = None
        minlength = None
        maxlength = None
        tagname = None

    def __init__(self, field, **kwds):
        if isinstance(field, Field):
            kwds["field"] = field
        else:
            kwds["field"] = Model(field, **kwds)
        super(List, self).__init__(**kwds)
        if not self.minlength and not self.tagname:
            self.required = False
        if self.minlength and not self.required:
            raise ValueError("List must be required if it has minlength")

    def _get_field(self):
        field = self.__dict__["field"]
        if not hasattr(field, "field_name"):
            field.field_name = self.field_name
        if not hasattr(field, "model_class"):
            field.model_class = self.model_class
        return field

    def _set_field(self, field):
        print 'List._set_field:', self, field
        self.__dict__["field"] = field

    field = property(_get_field, _set_field)

    def __get__(self, instance, owner=None):
        print 'List.__get__', 'self:', self, 'instance:', instance, 'owner:', owner
        
        print '\t calling super(List, self).__get__(instance, owner):', super(List, self).__get__
        val = super(List, self).__get__(instance, owner)
        print 'Back in Field.__get__'
        print '\t got return value:', val

        if val is not None:
            print '\t value was not None, returning it'
            return val

        print '\t Value was None, setting default value: []'
        self.__set__(instance, []) # Set the default value
        print 'Back in Field.__get__, from self.__set__'
        print '\t calling self.__get__ to get the default value back'
        res = self.__get__(instance, owner) # return the default value
        print 'Back in Field.__get__', 'returning result:', res
        return res

    def parse_child_node(self, obj, node):
        print "parse_child_node called on the 'List' Class"
        print 'self:', self
        print 'obj:', obj
        print 'node:', node
        #  If our children are inside a grouping tag, parse
        #  that first.  The presence of this is indicated by
        #  setting the empty list on the target object.
        if self.tagname:
            print 'self has tagname:', self.tagname
            print 'Calling super(List, self).__get__(obj):', super(List, self).__get__, obj
            val = super(List, self).__get__(obj)
            # ^^^ Why not call own __get__ ??
            # Anywhays requires this to return None before it tries to parse further on.
            print 'Got back value:', val            
            if val is None:                
                print 'node.nodeType:', node.nodeType
                if node.nodeType != node.ELEMENT_NODE:                
                    print 'Was an ELEMENT_NODE, returning PARSE_SKIP'
                    return dexml.PARSE_SKIP
                elif node.tagName == self.tagname:
                    print 'node.tagName:', node.tagName
                    print 'Setting default value on obj:', obj
                    self.__set__(obj, [])
                    print 'Returning dexml.PARSE_CHILDREN'
                    return dexml.PARSE_CHILDREN
                else:
                    print 'returning parse_skip 1'
                    return dexml.PARSE_SKIP
        #  Now we just parse each child node.
        tmpobj = _AttrBucket()
        print 'Calling parse_child_node:', tmpobj, node
        res = self.field.parse_child_node(tmpobj, node)
        print 'Got result back:', res
        
        if res is dexml.PARSE_MORE:
            raise ValueError("items in a list cannot return PARSE_MORE")
        if res is dexml.PARSE_DONE:
            items = self.__get__(obj)
            val = getattr(tmpobj, self.field_name)
            items.append(val)
            return dexml.PARSE_MORE
        else:
            print 'returning parse_skip 2'
            return dexml.PARSE_SKIP

    def parse_done(self, obj):
        items = self.__get__(obj)
        if self.minlength is not None and len(items) < self.minlength:
            raise dexml.ParseError("Field '%s': not enough items" % (self.field_name,))
        if self.maxlength is not None and len(items) > self.maxlength:
            raise dexml.ParseError("Field '%s': too many items" % (self.field_name,))

    def render_children(self, obj, items, nsmap):
        #  Create a generator that yields child data chunks, and validates
        #  the number of items in the list as it goes.  It allows any 
        #  iterable to be passed in, not just a list.
        def child_chunks():
            num_items = 0
            for item in items:
                num_items += 1
                if self.maxlength is not None and num_items > self.maxlength:
                    msg = "Field '%s': too many items" % (self.field_name,)
                    raise dexml.RenderError(msg)
                for data in self.field.render_children(obj, item, nsmap):
                    yield data
            if self.minlength is not None and num_items < self.minlength:
                msg = "Field '%s': not enough items" % (self.field_name,)
                raise dexml.RenderError(msg)

        chunks = child_chunks()
        #  Render each chunk, but suppress the wrapper tag if there's no data.
        try:
            data = chunks.next()
        except StopIteration:
            if self.tagname and self.required:
                yield "<%s />" % (self.tagname,)
        else:
            if self.tagname:
                yield "<%s>" % (self.tagname,)
            yield data
            for data in chunks:
                yield data
            if self.tagname:
                yield "</%s>" % (self.tagname,)


class Dict(Field):
    """Field subclass representing a dict of fields keyed by unique attribute value.

    This field corresponds to an indexed dict of other fields.  You would
    declare it like so:

      class MyObject(Model):
          name = fields.String(tagname = 'name')
          attr = fields.String(tagname = 'attr')

      class MyModel(Model):
          items = fields.Dict(fields.Model(MyObject), key = 'name')

    Corresponding to XML such as:

      <MyModel><MyObject><name>obj1</name><attr>val1</attr></MyObject></MyModel>


    The properties 'minlength' and 'maxlength' control the allowable size
    of the dict as in the List class.

    If 'unique' property is set to True, parsing will raise exception on
    non-unique key values.

    The 'dictclass' property controls the internal dict-like class used by
    the fielt.  By default it is the standard dict class.

    The 'tagname' property sets the 'wrapper' tag which acts as container
    for dict items, for example:

      from collections import defaultdict
      class MyObject(Model):
          name = fields.String()
          attr = fields.String()

      class MyDict(defaultdict):
          def __init__(self):
              super(MyDict, self).__init__(MyObject)

      class MyModel(Model):
          objects = fields.Dict('MyObject', key = 'name',
                                tagname = 'dict', dictclass = MyDict)

      xml = '<MyModel><dict><MyObject name="obj1">'\
            <attr>val1</attr></MyObject></dict></MyModel>'
      mymodel = MyModel.parse(xml)
      obj2 = mymodel['obj2']
      print(obj2.name)
      print(mymodel.render(fragment = True))

    This wrapper tag is always rendered, even if the dict is empty.  It is
    transparently removed when parsing.
    """

    class arguments(Field.arguments):
        field = None
        minlength = None
        maxlength = None
        unique = False
        tagname = None
        dictclass = dict

    def __init__(self, field, key, **kwds):
        if isinstance(field, Field):
            kwds["field"] = field
        else:
            kwds["field"] = Model(field, **kwds)
        super(Dict, self).__init__(**kwds)
        if not self.minlength and not self.tagname:
            self.required = False
        if self.minlength and not self.required:
            raise ValueError("Dict must be required if it has minlength")
        self.key = key

    def _get_field(self):
        field = self.__dict__["field"]
        if not hasattr(field, "field_name"):
            field.field_name = self.field_name
        if not hasattr(field, "model_class"):
            field.model_class = self.model_class
        return field

    def _set_field(self, field):
        self.__dict__["field"] = field

    field = property(_get_field, _set_field)

    def __get__(self, instance, owner=None):
        val = super(Dict, self).__get__(instance, owner)
        if val is not None:
            return val

        class dictclass(self.dictclass):
            key = self.key

            def __setitem__(self, key, value):
                keyval = getattr(value, self.key)
                if keyval and keyval != key:
                    raise ValueError('Key field value does not match dict key')
                setattr(value, self.key, key)
                super(dictclass, self).__setitem__(key, value)

        self.__set__(instance, dictclass())
        return self.__get__(instance, owner)

    def parse_child_node(self, obj, node):
        #  If our children are inside a grouping tag, parse
        #  that first.  The presence of this is indicated by
        #  setting an empty dict on the target object.
        if self.tagname:
            val = super(Dict, self).__get__(obj)
            if val is None:
                if node.nodeType != node.ELEMENT_NODE:
                    return dexml.PARSE_SKIP
                elif node.tagName == self.tagname:
                    self.__get__(obj)
                    return dexml.PARSE_CHILDREN
                else:
                    return dexml.PARSE_SKIP
        #  Now we just parse each child node.
        tmpobj = _AttrBucket()
        res = self.field.parse_child_node(tmpobj, node)
        if res is dexml.PARSE_MORE:
            raise ValueError("items in a dict cannot return PARSE_MORE")
        if res is dexml.PARSE_DONE:
            items = self.__get__(obj)
            val = getattr(tmpobj, self.field_name)
            try:
                key = getattr(val, self.key)
            except AttributeError:
                raise dexml.ParseError("Key field '%s' required but not found in dict value" % (self.key, ))
            if self.unique and key in items:
                raise dexml.ParseError("Key '%s' already exists in dict" % (key,))
            items[key] = val
            return dexml.PARSE_MORE
        else:
            return dexml.PARSE_SKIP

    def parse_done(self, obj):
        items = self.__get__(obj)
        if self.minlength is not None and len(items) < self.minlength:
            raise dexml.ParseError("Field '%s': not enough items" % (self.field_name,))
        if self.maxlength is not None and len(items) > self.maxlength:
            raise dexml.ParseError("Field '%s': too many items" % (self.field_name,))

    def render_children(self, obj, items, nsmap):
        if self.minlength is not None and len(items) < self.minlength:
            raise dexml.RenderError("Field '%s': not enough items" % (self.field_name,))
        if self.maxlength is not None and len(items) > self.maxlength:
            raise dexml.RenderError("too many items")
        if self.tagname:
            children = "".join(data for item in items.values() for data in self.field.render_children(obj, item, nsmap))
            if not children:
                if self.required:
                    yield "<%s />" % (self.tagname,)
            else:
                yield children.join(('<%s>' % self.tagname, '</%s>' % self.tagname))
        else:
            for item in items.values():
                for data in self.field.render_children(obj, item, nsmap):
                    yield data


class Choice(Field):
    """Field subclass accepting any one of a given set of Model fields."""

    class arguments(Field.arguments):
        fields = []

    def __init__(self, *fields, **kwds):
        real_fields = []
        for field in fields:
            if isinstance(field, Model):
                real_fields.append(field)
            elif isinstance(field, basestring):
                real_fields.append(Model(field))
            else:
                raise ValueError("only Model fields are allowed within a Choice field")
        kwds["fields"] = real_fields
        super(Choice, self).__init__(**kwds)

    def parse_child_node(self, obj, node):
        for field in self.fields:
            field.field_name = self.field_name
            field.model_class = self.model_class
            res = field.parse_child_node(obj, node)
            if res is dexml.PARSE_MORE:
                raise ValueError("items in a Choice cannot return PARSE_MORE")
            if res is dexml.PARSE_DONE:
                return dexml.PARSE_DONE
        else:
            return dexml.PARSE_SKIP

    def render_children(self, obj, item, nsmap):
        if item is None:
            if self.required:
                raise dexml.RenderError("Field '%s': required field is missing" % (self.field_name,))
        else:
            for data in item._render(nsmap=nsmap):
                yield data


class XmlNode(Field):
    class arguments(Field.arguments):
        tagname = None
        encoding = None

    def __set__(self, instance, value):
        if isinstance(value, basestring):
            if isinstance(value, unicode) and self.encoding:
                value = value.encode(self.encoding)
            doc = dexml.minidom.parseString(value)
            value = doc.documentElement
        if value is not None and value.namespaceURI is not None:
            nsattr = "xmlns"
            if value.prefix:
                nsattr = ":".join((nsattr, value.prefix,))
            value.attributes[nsattr] = value.namespaceURI
        return super(XmlNode, self).__set__(instance, value)

    def parse_child_node(self, obj, node):
        if self.tagname is None or self._check_tagname(node, self.tagname):
            self.__set__(obj, node)
            return dexml.PARSE_DONE
        return dexml.PARSE_SKIP

    @classmethod
    def render_children(cls, obj, val, nsmap):
        if val is not None:
            yield val.toxml()

