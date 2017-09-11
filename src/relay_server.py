import socket
import queue
import threading


class Request:
    ip_addr = None
    port = None
    payload = None

    def __init__(self, ip_addr=None, port=None, payload=None):
        self.ip_addr = ip_addr
        self.port = port
        self.payload = payload


def read_relay_socket(relay_host: socket.socket, request_queue: queue.Queue):
    buffer = b""
    while True:
        buffer += relay_host.recv(9)
        if buffer == b"":
            break  # TODO Dette betyr at tilkoblingen er brutt

        while len(buffer) < 9:
            buffer += relay_host.recv(9)

        header = buffer[:9]
        buffer = buffer[9:]  # Fjern header-delen fra bufferet, den er behandlet

        if header[0] == 0x02:
            request = Request()
            request.ip_addr = header[1:5]
            request.port = header[5:7]
            payload_len = header[7:9]

            buffer += relay_host.recv(payload_len)
            while len(buffer) < payload_len:
                buffer += relay_host.recv(payload_len)

            request.payload = buffer[:payload_len]
            buffer = buffer[payload_len:]  # Fjern data i bufferet som vi har behandlet

            request_queue.put(request)

        elif header[0] == 0x01:
            # TODO Svar på keepalive?
            pass

        else:
            print("Unknown packet type: {}".format(buffer[0]))


relay_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_host.connect(("tihlde.org", 9877))

request_queue = queue.Queue()
threading.Thread(target=read_relay_socket, args=(relay_host, request_queue)).start()

while True:
    request = request_queue.get()

    print("Request from relay host: {}".format(request.payload.split(b"\r\n")[0]))

    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.connect(("127.0.0.1", 80))
    local_server.send(request.payload)

    response = local_server.recv(4096)
    while True:
        response_part = local_server.recv(4096)
        if response_part == b"":
            break

        response += response_part

    local_server.close()

    print("Response from local server: {}".format(response.split(b"\r\n")[0]))

    while len(response) > 0:
        part_response = response[:0xffff]
        response_message = b"\x02"
        response_message += request.ip_addr
        response_message += request.port
        response_message += (b"\x00" * 2 + len(part_response).to_bytes(2, 'big'))[-2:]
        response_message += part_response

        relay_host.send(response_message)
        response = response[0xffff:]

relay_host.close()
