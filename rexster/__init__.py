#!/usr/bin/env python
#-*- coding:utf-8 -*-

import requests
import simplejson


class RexsterException(BaseException):
    pass


class RexsterServer(object):
    """An class that implements a way to connect to
    a Rexster Instance from Python"""
    def __init__(self, host):
        self.host = host
        r = requests.get(host)
        if r.error:
            raise RexsterException("Could not connect to a Rexster server")
        else:
            self.data = simplejson.loads(r.content)

    def name(self):
        """Return server name"""
        return self.data.get('name')

    def version(self):
        """Return server version"""
        return self.data.get('version')

    def uptime(self):
        """Return server uptime"""
        return self.data.get('upTime')

    def graphs(self):
        """Returns a list of available graphs"""
        return self.data.get('graphs')


class Element(object):
    """An class defining an Element object composed
    by a collection of key/value properties for the
    Rexster compatible database"""

    def __init__(self, graph, url):
        """Creates a new element
        @params graph: The graph object the element belongs
        @params url: The element REST URL

        @returns The element"""
        self.url = url
        self.graph = graph
        r = requests.get(url)
        content = simplejson.loads(r.content)
        properties = content.get('results')
        if not properties:
            raise RexsterException(content['message'])
        self.properties = {}
        for key, value in properties.iteritems():
            self.properties[key] = value
        self._id = self.properties.get('_id')

    def getId(self):
        """Returns the unique identifier of the element

        @returns The unique identifier of the element"""
        return self._id

    def setProperty(self, key, value):
        """Sets the property of the element to the given value
        @params key: The property key to set
        @params value: The value to set"""
        r = requests.post(self.url, data={key: value})
        if r.error:
            error_msg = simplejson.loads(r.content)['message']
            raise RexsterException(error_msg)
        self.properties[key] = value

    def getProperty(self, key):
        """Gets the value of the property for the given key
        @params key: The key which value is being retrieved

        @returns The value of the property with the given key"""
        r = requests.get(self.url)
        properties = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(properties['message'])
        else:
            return properties['results'].get(key)

    def getPropertyKeys(self):
        """Returns a set with the property keys of the element

        @returns Set of property keys"""
        r = requests.get(self.url)
        properties = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(properties['message'])
        else:
            return properties['results'].keys()

    def removeProperty(self, key):
        """Removes the value of the property for the given key
        @params key: The key which value is being removed"""
        r = requests.delete(self.url, params=key)
        if r.error:
            error_msg = simplejson.loads(r.content)['message']
            raise RexsterException(error_msg)
        self.properties.pop(key)


class Vertex(Element):
    """An abstract class defining a Vertex object representing
    a node of the graph with a set of properties"""

    def __init__(self, graph, _id):
        """Creates a new vertex
        @params graph: The graph object the vertex belongs
        @params _id: The vertex unique identifier

        @returns The vertex"""
        url = "%s/vertices/%s" % (graph.url, _id)
        super(Vertex, self).__init__(graph, url)

    def _generator(self, generator):
        for item in generator:
            yield Edge(self.graph, item.get('_id'))

    def getOutEdges(self, label=None):
        """Gets all the outgoing edges of the node. If label
        parameter is provided, it only returns the edges of
        the given label
        @params label: Optional parameter to filter the edges

        @returns A generator function with the outgoing edges"""
        if label:
            url = "%s/outE?_label=%s" % (self.url, label)
        else:
            url = "%s/outE" % self.url
        r = requests.get(url)
        return self._generator(simplejson.loads(r.content)['results'])

    def getInEdges(self, label=None):
        """Gets all the incoming edges of the node. If label
        parameter is provided, it only returns the edges of
        the given label
        @params label: Optional parameter to filter the edges

        @returns A generator function with the incoming edges"""
        if label:
            url = "%s/inE?_label=%s" % (self.url, label)
        else:
            url = "%s/inE" % self.url
        r = requests.get(url)
        return self._generator(simplejson.loads(r.content)['results'])

    def getBothEdges(self, label=None):
        """Gets all the edges of the node. If label
        parameter is provided, it only returns the edges of
        the given label
        @params label: Optional parameter to filter the edges

        @returns A generator function with the incoming edges"""
        if label:
            url = "%s/bothE?_label=%s" % (self.url, label)
        else:
            url = "%s/bothE" % self.url
        r = requests.get(url)
        return self._generator(simplejson.loads(r.content)['results'])

    def __str__(self):
        return "Vertex %s: %s" % (self._id, self.properties)


class Edge(Element):
    """An abstract class defining a Edge object representing
    a relationship of the graph with a set of properties"""

    def __init__(self, graph, _id):
        """Creates a new edge
        @params graph: The graph object the edge belongs
        @params _id: The edge unique identifier

        @returns The edge"""
        url = "%s/edges/%s" % (graph.url, _id)
        super(Edge, self).__init__(graph, url)

    def getOutVertex(self):
        """Returns the origin Vertex of the relationship

        @returns The origin Vertex"""
        return Vertex(self.graph, self.properties.get('_outV'))

    def getInVertex(self):
        """Returns the target Vertex of the relationship

        @returns The target Vertex"""
        return Vertex(self.graph, self.properties.get('_inV'))

    def getLabel(self):
        """Returns the label of the relationship

        @returns The edge label"""
        return self.properties.get('_label')

    def __str__(self):
        return "Edge %s: %s" % (self._id, self.properties)


class RexsterGraph(object):

    def __init__(self, server, name):
        self.server = server
        self.name = name
        self.url = "%s/%s" % (server.host, name)

    def getMetadata(self):
        r = requests.get(self.url)
        return simplejson.loads(r.content)

    def addVertex(self, _id=None):
        """Adds a new vertex
        @params _id: Node unique identifier

        @returns The created Vertex or None"""
        if _id:
            url = "%s/vertices/%s" % (self.url, _id)
        else:
            url = "%s/vertices" % (self.url)
        r = requests.post(url)
        if r.error:
            raise RexsterException("Could not create vertex")
        else:
            properties = simplejson.loads(r.content)['results']
            return Vertex(self, properties['_id'])

    def getVertex(self, _id):
        """Retrieves an existing vertex from the graph
        @params _id: Node unique identifier

        @returns The requested Vertex or None"""
        try:
            return Vertex(self, _id)
        except RexsterException:
            return None

    def getVertices(self):
        """Returns an iterator with all the vertices"""
        url = "%s/vertices" % self.url
        r = requests.get(url)
        for vertex in simplejson.loads(r.content)['results']:
            yield Vertex(self, vertex.get('_id'))

    def removeVertex(self, vertex):
        """Removes the given vertex
        @params vertex: Node to be removed"""
        _id = vertex.getId()
        url = "%s/vertices/%s" % (self.url, _id)
        r = requests.delete(url)
        if r.error:
            raise RexsterException("Could not delete vertex")

    def addEdge(self, outV, inV, label):
        """Creates a new edge
        @params outVertex: Edge origin Vertex
        @params inVertex: Edge target vertex
        @params label: Edge label

        @returns The created Edge object"""
        url = "%s/edges?_outV=%s&_inV=%s&_label=%s" % (self.url,
                                                    outV.getId(),
                                                    inV.getId(),
                                                    label)
        data = dict(_outV=outV.getId(),
                    _inV=inV.getId(),
                    _label=label)
        r = requests.post(url, data=data)
        if r.error:
            raise RexsterException("Could not create the edge")
        properties = simplejson.loads(r.content)['results']
        return Edge(self, properties['_id'])

    def getEdges(self):
        """Returns an iterator with all the edges"""
        url = "%s/edges" % self.url
        r = requests.get(url)
        content = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(content['message'])
        else:
            for edge in content['results']:
                yield Edge(self, edge.get('_id'))

    def getEdge(self, _id):
        """Retrieves an existing edge from the graph
        @params _id: Edge unique identifier

        @returns The requested Edge"""
        try:
            return Edge(self, _id)
        except RexsterException:
            return None

    def removeEdge(self, edge):
        """Removes the given edge
        @params edge: The edge to be removed"""
        _id = edge.getId()
        url = "%s/edges/%s" % (self.url, _id)
        r = requests.delete(url)
        if r.error:
            raise RexsterException("Could not delete edge")


class Index(object):
    """An class containing all the methods needed by an
    Index object"""

    def __init__(self, graph, indexName, indexClass, indexType):
        self.graph = graph
        self.indexName = indexName
        self.indexType = indexType
        indexClass = (indexClass.split('.')[-1]).lower()
        self.indexClass = indexClass
        self.url = "%s/indices/%s" % (self.graph.url,
                                    self.indexName)

    def count(self, key, value):
        """Returns the number of elements indexed for a
        given key-value pair
        @params key: Index key string
        @params outVertex: Index value string

        @returns The number of elements indexed"""
        url = "%s/count" % self.url
        r = requests.get(url, params={'key': key,
                                    'value': value})
        content = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(content['message'])
        return content['totalSize']

    def getIndexName(self):
        """Returns the name of the index

        @returns The name of the index"""
        return self.indexName

    def getIndexClass(self):
        """Returns the index class (VERTICES or EDGES)

        @returns The index class"""
        return self.indexClass

    def getIndexType(self):
        """Returns the index type (AUTOMATIC or MANUAL)

        @returns The index type"""
        return self.indexType

    def put(self, key, value, element):
        """Puts an element in an index under a given
        key-value pair
        @params key: Index key string
        @params value: Index value string
        @params element: Vertex or Edge element to be indexed"""
        if isinstance(element, Vertex):
            klass = 'vertex'
        elif isinstance(element, Edge):
            klass = 'edge'
        else:
            raise RexsterException("Unknown element type")
        data = {'key': key,
                'value': value,
                'class': klass,
                'id': element.getId()}
        r = requests.post(self.url, data)
        if r.error:
            error_msg = simplejson.loads(r.content)['message']
            raise RexsterException(error_msg)

    def get(self, key, value):
        """Gets an element from an index under a given
        key-value pair
        @params key: Index key string
        @params value: Index value string
        @returns A generator of Vertex or Edge objects"""
        r = requests.get(self.url, params={'key': key,
                                        'value': value})
        content = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(content['message'])
        for item in content['results']:
            if self.indexClass == 'vertex':
                yield Vertex(self.graph, item.get('_id'))
            else:
                yield Edge(self.graph, item.get('_id'))

    def remove(self, key, value, element):
        """Removes an element from an index under a given
        key-value pair
        @params key: Index key string
        @params value: Index value string
        @params element: Vertex or Edge element to be removed"""
        if isinstance(element, Vertex):
            klass = 'vertex'
        elif isinstance(element, Edge):
            klass = 'edge'
        else:
            raise RexsterException("Unknown element to be deleted")
        _id = element.getId()
        data = {'class': klass, 'key': key, 'value': value, 'id': _id}
        r = requests.delete(self.url, params=data)
        if r.error:
            raise RexsterException("Could not delete element")

    def __str__(self):
        return "Index %s (%s, %s)" % (self.indexName,
                                    self.indexClass,
                                    self.indexType)


class AutomaticIndex(Index):

    def getAutoIndexKeys(self):
        url = "%s/keys" % self.url
        r = requests.get(url)
        content = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(content['message'])
        return content['results']


class RexsterIndexableGraph(RexsterGraph):
    """An class containing the specific methods
    for indexable graphs"""

    def __createIndex(self, indexName, indexClass, indexType, autoKeys=[]):
        indexClass = indexClass.lower()
        if indexClass != 'vertex' and indexClass != 'edge':
            raise RexsterException("%s is not a valid indexClass" \
                                    % indexClass)
        url = "%s/indices/%s" % (self.url, indexName)
        data = {'class': indexClass, 'type': indexType}
        if indexType == 'automatic':
            data['keys'] = autoKeys
        r = requests.post(url, data=data)
        content = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(content['message'])
        return content['results']

    def createManualIndex(self, indexName, indexClass):
        """Creates a manual index
        @params name: The index name
        @params indexClass: vertex or edge

        @returns The created Index"""
        content = self.__createIndex(indexName, indexClass, 'manual')
        return Index(self, content['name'], content['class'], content['type'])

    def createAutomaticIndex(self, indexName, indexClass, autoKeys=[]):
        """Creates an automatic index
        @params name: The index name
        @params indexClass: vertex or edge
        @params autoKeys: A list of the automatically indexed properties

        @returns The created AutomaticIndex"""
        content = self.__createIndex(indexName, indexClass, 'automatic',
                                    autoKeys)
        return AutomaticIndex(self, content['name'], content['class'],
                            content['type'])

    def getIndices(self):
        """Returns a generator function over all the existing indexes

        @returns A generator function over all rhe Index objects"""
        url = "%s/indices" % self.url
        r = requests.get(url)
        content = simplejson.loads(r.content)
        if r.error:
            raise RexsterException(content['message'])
        for index in content['results']:
            yield Index(self, index['name'], index['class'], index['type'])

    def getIndex(self, indexName, indexClass):
        """Retrieves an index with a given index name and class
        @params indexName: The index name
        @params indexClass: VERTICES or EDGES

        @return The Index object or None"""
        url = "%s/indices/%s" % (self.url, indexName)
        r = requests.get(url)
        content = simplejson.loads(r.content)
        if r.error:
            return None
        if content['type'] == 'automatic':
            return AutomaticIndex(self, content['name'],
                                content['class'], content['type'])
        else:
            return Index(self, content['name'], content['class'],
                        content['type'])

    def dropIndex(self, indexName):
        """Removes an index with a given indexName
        @params indexName: The index name"""
        url = "%s/indices/%s" % (self.url, indexName)
        r = requests.delete(url)
        if r.error:
            content = simplejson.loads(r.content)
            raise RexsterException(content['message'])
