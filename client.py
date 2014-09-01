"""NoSQL client."""

import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 50505))
    s.sendall(b'GET;foo;;')
    response = s.recv(4096)
    s.close()
    print(response)


if __name__ == '__main__':
    main()
