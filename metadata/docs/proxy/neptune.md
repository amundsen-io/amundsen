# Neptune

## Documentation

In particular, see [Gremlin differences](https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html),
and [Gremlin sessions](https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-sessions.html).

And any time you see docs from Kelvin (like the PRACTICAL GREMLIN book or lots of stackoverflow) pay
attention, he works for AWS on Neptune.

## IAM authentication

The gremlin transport is usually websockets, and the requests-aws4auth library we use elsewhere is
for requests, which does not support websockets at all.  So we rolled our in `aws4authwebsocket`.
The saving grace of websockets and IAM is that the IAM authentication really only applies to the
initialization request and the rest of the data flows over the existing TCP connection.  The usual
gremlin-python transport is Tornado, which was a huge pain to try and insinuate the aws4
autentication in to, so we use the websockets-client library instead.

## How to get a gremlin console for AWS

They have pretty decent recipe [here](https://docs.aws.amazon.com/neptune/latest/userguide/iam-auth-connecting-gremlin-java.html)
