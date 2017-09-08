import socket
import threading


relay_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_server.bind(("", 9877))
relay_server.listen(1)

relay_server_conn, relay_server_addr = relay_server.accept()
print("Recieved connection from relayed server at {}".format(relay_server_addr))

relay_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_client.bind(("", 9878))
relay_client.listen(1)


def serve_connection(client_conn):
    while True:
        request = client_conn.recv(4096)
        print("Request from client: {}".format(request.split(b"\r\n")[0]))

        relay_server_conn.send(request)
        response = relay_server_conn.recv(4096)
        print("Response from relayed server: {}".format(response.split(b"\r\n")[0]))

        client_conn.send(response)

    client_conn.close()


connection_threads = []
while True:
    client_conn, client_addr = relay_client.accept()
    print("Recieved connection from client at {}".format(client_addr))
    thread = threading.Thread(target=serve_connection, args=(client_conn, ))
    connection_threads.append(thread)
    thread.start()


relay_client.close()
relay_server.close()
