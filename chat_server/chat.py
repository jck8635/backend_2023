import socket
import select
import threading
from queue import Queue

HOST = '127.0.0.1'
PORT = 19171
NUM_WORKER_THREADS = 2

message_queue = Queue()
lock = threading.Lock()

def worker_thread():
    while True:
        message = message_queue.get()
        print(f"Processing message: {message}")
        message_queue.task_done()

# 쓰레드 생성 및 시작
for _ in range(NUM_WORKER_THREADS):
    thread = threading.Thread(target=worker_thread)
    thread.daemon = True
    thread.start()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# 연결된 클라이언트를 추적하기 위한 리스트
client_sockets = [server_socket]

print(f"Server listening on {HOST}:{PORT}")

try:
    while True:
        # I/O 멀티플렉싱을 위해 select 사용
        readable, _, _ = select.select(client_sockets, [], [])

        for sock in readable:
            if sock == server_socket:
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")
                client_sockets.append(client_socket)

            else:
                data = sock.recv(1024)
                if not data:
                    print(f"Client {sock.getpeername()} disconnected")
                    sock.close()
                    client_sockets.remove(sock)
                else:
                    # 받은 메시지를 처리하기 위해 큐에 추가
                    with lock:
                        message_queue.put(data)

finally:
    for sock in client_sockets[1:]:
        sock.close()

    server_socket.close()
