# pyrelay
Relaying and multiplexing of TCP streams to a server behind a NAT


### What?
Server S is hosting some kind of service (HTTP, SSH etc.) behind a NAT which cannot be port forwarded, meaning client C can't communicate with S unless S initiates the connection. A relay server R is located on a public static IP address, and runs relay_host.py which listens on ports Pc and Ps. S starts relay_server.py which connects to R on port Ps. C connects to R on port Pc. C sends requests to R:Pc, and R relays it to S through the connection made by S to R:Ps. The relay_server.py program then forwards the request to the local service on S, and sends the response back to R, which in turn relays the response back to C.
