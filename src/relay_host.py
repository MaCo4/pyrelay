import queue
import socket
import threading


def serve_client_conn(client_conn: socket.socket):
    while True:
        request = b""
        while True:
            request_part = client_conn.recv(4096)
            if not request_part:
                break
            request += request_part

        print("Request from client: {}".format(request.split(b"\r\n")[0]))

        send_to_server(client_conn, request)

        response = relay_server_conn.recv(4096)
        print("Response from relayed server: {}".format(response.split(b"\r\n")[0]))

        client_conn.send(response)

    client_conn.close()


def send_to_server(source, data):
    if len(data) > 0xffff:
        return

    source_addr = source.getpeername()

    message = b"\x02"                                             # Packet type (0x02 for normal data), 1 byte
    message += socket.inet_aton(source_addr[0])                   # Source IP address, 4 bytes
    message += source_addr[1].to_bytes(2, "big")                  # Source port number, 2 bytes
    message += (b"\x00" * 2 + len(data).to_bytes(2, "big"))[-2:]  # Payload length, 2 bytes
    message += data                                               # Payload

    server_message_queue.put(message)


def process_send_queue(server_connection: socket.socket, server_message_queue: queue.Queue):
    while True:
        try:
            message = server_message_queue.get(timeout=10)
            server_connection.send(message)
        except queue.Empty:
            pass
            # TODO Send keep-alive pakke hvis ingenting annet er sendt på en stund


relay_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_server.bind(("", 9877))
relay_server.listen(1)

relay_server_conn, relay_server_addr = relay_server.accept()
server_message_queue = queue.Queue()
print("Received connection from endpoint server at {}".format(relay_server_addr))
threading.Thread(target=process_send_queue, args=(relay_server_conn, server_message_queue)).start()

relay_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_client.bind(("", 9878))
relay_client.listen(1)

connection_threads = []
while True:
    client_conn, client_addr = relay_client.accept()
    print("Recieved connection from client at {}".format(client_addr))
    thread = threading.Thread(target=serve_client_conn, args=(client_conn,))
    connection_threads.append(thread)
    thread.start()

relay_client.close()
relay_server.close()
