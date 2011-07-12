python-rexster
==============

:synopsis: Implements a client over Rexster (https://github.com/tinkerpop/rexster/) providing the Python developer an easy way to interact with the databases supported.

The layer follows the pyblueprints graph model interface letting the programmer work in the same way, no matter which underlying graph database is being used.

Installation
------------
The easiest way to get python-rexster installed in your virtualenv is by:

 pip install python-rexster


Usage
-----

Connecting to a Rexster instance

>>> from rexster import RexsterServer, RexsterGraph 
>>> #Connecting to server
>>> HOST = 'http://localhost:8182'
>>> server = RexsterServer(HOST)
>>> #List graphs availbale in server
>>> server.graphs()
[u'tinkergraph', u'gratefulgraph', u'tinkergraph-readonly', u'sailgraph', u'emptygraph']
>>> #Connecting to a given graph
>>> graph = RexsterIndexableGraph(server, 'tinkergraph')
