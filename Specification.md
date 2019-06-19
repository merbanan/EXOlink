EXOLine-TCP documentation
=========================

The document describes the current understanding of the EXOLine-TCP IPv4 protocol.

General description
-------------------

The protocol uses a synchronous client/server approch. The tcp port used is 26486.
The data payload syntax of server answers depends on the sent client query. So you
have to keep track of your query and tcp-connection to process the answer. It is assumed
that EXOLine-TCP is related to EXOLine (serial) and thus design limitations from that protocol
are present in EXOLine-TCP.



Message structure
-----------------

The messages are byte-based and formed like the following:

| Position      | Value         | Meaning|
| ------------- |:-------------:| -----:|
| 0             | 0x3c/0x3d     | Message start value (Client/Server) |
| X             | ...           | Payload (depends on command) |
| Last-1        | XORSUM        | Xorsum of all bytes after start value until XORSUM byte |
| Last          | 0x3e          | Message stop value |

### Escape-value

If any start, stop or escape value is present in the Payload or XORSUM it is
replaced by an escape value (**0x1B**) and the bit-wise inverse of the actual value.
This is done by both clients and serves.

As example here is a server response for a temperature reading.

[ 3d 05 00 14 c3 ae 41 *1b* c2 3e ] (escape value in cursive)

The payload is [ 05 00 14 c3 ae 41 ] and its xorsum is 0x3D (server start value).
Thus an escape value and the inverse value (0xC2) is inserted instead.

Encryption
----------

It is possible to use encryption, the crypto is called Saphire and is currently not documented.
