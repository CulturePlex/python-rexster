#!/usr/bin/env python
#-*- coding:utf-8 -*-


##########################################################################
# This test has been performed with a default rexster-0.4.1 distribution #
##########################################################################

import unittest
from rexster import *

HOST = 'http://localhost:8182'
GRAPH = 'tinkergraph'


class RequestServerTestSuite(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testServerInvalidConnection(self):
        self.assertRaises(RexsterException,
                            RexsterServer,
                            'http://invalidurl')

    def testServerValidConnection(self):
        server = RexsterServer(HOST)
        self.assertIsInstance(server, RexsterServer)

    def testGetServerName(self):
        server = RexsterServer(HOST)
        self.assertEqual(server.name(), u'Rexster: A RESTful Graph Shell')

    def testGetServerGraphs(self):
        server = RexsterServer(HOST)
        sampleGraphs = [u'tinkergraph', u'gratefulgraph',
                        u'tinkergraph-readonly',
                        u'sailgraph', u'emptygraph']

        self.assertEqual(server.graphs(), sampleGraphs)

    def testAddRemoveVertex(self):
        server = RexsterServer(HOST)
        graph = RexsterGraph(server, GRAPH)
        vertex = graph.addVertex()
        self.assertIsInstance(vertex, Vertex)
        _id = vertex.getId()
        graph.removeVertex(vertex)
        self.assertIsNone(graph.getVertex(_id))

    def testVertexMethods(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterGraph(server, GRAPH)
        vertex = graph.getVertex(1)
        self.assertIsInstance(vertex, Vertex)
        self.assertEqual(vertex.getId(), '1')
        edge = list(vertex.getBothEdges())[0]
        self.assertIsInstance(edge, Edge)
        edge = list(vertex.getOutEdges())[0]
        self.assertIsInstance(edge, Edge)
        edges = list(vertex.getInEdges())
        self.assertEqual(edges, [])

    def testElementProperties(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterGraph(server, GRAPH)
        vertex = graph.getVertex(1)
        defaultProperties = ['age', '_type', '_id', 'name']
        self.assertEqual(vertex.getPropertyKeys(), defaultProperties)
        self.assertEqual(vertex.getProperty('name'), 'marko')
        vertex.setProperty('name', 'pablito')
        self.assertEqual(vertex.getProperty('name'), 'pablito')
        vertex.removeProperty('name')
        self.assertNotIn('name', vertex.getPropertyKeys())
        vertex.setProperty('name', 'marko')
        self.assertEqual(vertex.getProperty('name'), 'marko')

    def testEdgeMethods(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterGraph(server, GRAPH)
        edge = graph.getEdge(7)
        outVertex = edge.getOutVertex()
        self.assertIsInstance(outVertex, Vertex)
        self.assertEqual(outVertex.getId(), '1')
        inVertex = edge.getInVertex()
        self.assertIsInstance(inVertex, Vertex)
        self.assertEqual(inVertex.getId(), '2')
        self.assertEqual(edge.getLabel(), 'knows')

    def testAddRemoveEdges(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterGraph(server, GRAPH)
        v1 = graph.getVertex(1)
        v2 = graph.getVertex(2)
        newEdge = graph.addEdge(v1, v2, 'myLabel')
        self.assertIsInstance(newEdge, Edge)
        _id = newEdge.getId()
        graph.removeEdge(newEdge)
        self.assertIsNone(graph.getEdge(_id))

    def testGetVertices(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterGraph(server, GRAPH)
        vertices = list(graph.getVertices())
        vertex = vertices[0]
        self.assertIsInstance(vertex, Vertex)

    def testGetEdges(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterGraph(server, GRAPH)
        edges = list(graph.getEdges())
        edge = edges[0]
        self.assertIsInstance(edge, Edge)

    def testAddRemoveManualIndex(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterIndexableGraph(server, GRAPH)
        index = graph.createManualIndex('myManualIndex', 'vertex')
        self.assertIsInstance(index, Index)
        index = graph.getIndex('myManualIndex', 'vertex')
        self.assertIsInstance(index, Index)
        graph.dropIndex('myManualIndex')
        self.assertIsNone(graph.getIndex('myManualIndex', 'vertex'))

    def testAddRemoveAutomaticIndex(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterIndexableGraph(server, GRAPH)
        keys = ['key1', 'key2']
        index = graph.createAutomaticIndex('myAutoIndex', 'vertex', keys)
        self.assertIsInstance(index, Index)
        index = graph.getIndex('myAutoIndex', 'vertex')
        self.assertIsInstance(index, Index)
        autoKeys = index.getAutoIndexKeys()
        #TODO self.assertIn('key1', autoKeys)
        #TODO self.assertIn('key2', autoKeys)
        graph.dropIndex('myAutoIndex')
        self.assertIsNone(graph.getIndex('myAutoIndex', 'vertex'))

    def testIndexing(self):
        server = RexsterServer('http://localhost:8182')
        graph = RexsterIndexableGraph(server, GRAPH)
        index = graph.createManualIndex('myManualIndex', 'vertex')
        vertex = graph.getVertex(1)
        index.put('key1', 'value1', vertex)
        self.assertEqual(index.count('key1', 'value1'), 1)
        self.assertEqual(index.getIndexName(), 'myManualIndex')
        self.assertEqual(index.getIndexClass(), 'vertex')
        self.assertEqual(index.getIndexType(), 'manual')
        vertex2 = list(index.get('key1', 'value1'))[0]
        self.assertEqual(vertex.getId(), vertex2.getId())
        index.remove('key1', 'value1', vertex)
        self.assertEqual(index.count('key1', 'value1'), 0)
        graph.dropIndex('myManualIndex')

if __name__ == "__main__":
    unittest.main()
