import socket


relay_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_host.connect(("tihlde.org", 9877))
while True:
    request = relay_host.recv(4096)
    print("Request from relay host: {}".format(request.split(b"\r\n")[0]))

    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.connect(("127.0.0.1", 80))

    local_server.send(request)
    response = local_server.recv(4096)
    print("Response from local server: {}".format(response.split(b"\r\n")[0]))

    relay_host.send(response)
    local_server.close()

relay_host.close()
