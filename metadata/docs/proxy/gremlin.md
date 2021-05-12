# Gremlin Proxy

## What the heck is Gremlin?  Why is it named Gremlin?

[Gremin](https://tinkerpop.apache.org/gremlin.html) is the graph traversal language of
[Apache TinkerPop](https://tinkerpop.apache.org/).  Why not Gremlin?

## Documentation

The docs linked from [Gremin](https://tinkerpop.apache.org/gremlin.html) are a good start.   For
example, the [Getting Started](http://tinkerpop.apache.org/docs/current/tutorials/getting-started/)
and the [PRACTICAL GREMLIN book](http://kelvinlawrence.net/book/Gremlin-Graph-Guide.html)

## How to target a new Gremlin backend

This is not an exhaustive list, but some issues we've found along the way:
  - Are there restricted property names?  For example JanusGraph does not allow a property named
  `key`, so the base Gremlin proxy has a property named `key_property_name` which is set to `_key`
  for JanusGraph but `key` for others.
  - Is there database management required?  For example AWS Neptune does now allow explicit creation
  of indexes, nor assigning data types to properties, but JanusGraph does and practically requires
  the creation of indexes.
  - Are there restrictions on the methods? For example, JanusGraph accepts any of the Java or Groovy
  names, but Neptune accepts a strict subset. JanusGraph can install any script engine, e.g. to
  allow Python lambdas but Neptune only allows Groovy lambdas.

Other differences between Janusgraph and Neptune can be found here:
https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html
