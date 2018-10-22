import sys
import socket
import threading
import http
import email.message

_MAXLINE = 65536

def main():
    if len(sys.argv) < 2:
        print("no port given, default port is 8080")
        port = 8080
    else:
        port = int(sys.argv[1])

    try:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recv_socket.bind(("", port))
        recv_socket.listen()
        print("listen on port: %d" % port)
    except socket.error as error:
        if recv_socket:
            recv_socket.close()
        print("Could not open socket: %s" % error.strerror)

    while True:
        req, address = recv_socket.accept()
        handle_request(req, address)


def handle_request(req, address):
    threading.Thread(target=request_handle_routine, args=(req, address)).start()


def request_handle_routine(req: socket.socket, address):
    rawData, host = parse_request(req)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 80))
        s.sendall(bytes(rawData, 'utf8'))

        print('connected to host %s' % host)

        while True:
            #if server don't close tcp connection, this will failed
            data = s.recv(_MAXLINE)
            if len(data) > 0:
                req.sendall(data)
            else:
                break
        s.close()
        req.close()
        print('disconnect to host %s' % host)
            
    except socket.error as error:
        if s:
            s.close()
        if req:
            req.close()
        print("connect host %s failed due to %s" % (host, error.strerror))

def parse_request(req: socket.socket):
    reqData = ''
    rfile = req.makefile()
    first_line = rfile.readline(_MAXLINE+1)
    reqData += first_line
    first_line = first_line.rstrip('\r\n')
    words = first_line.split()
    if len(words) == 3:
        method, path, version = words
    elif len(words) == 2:
        method, path = words
    
    header_lines = []
    while True:
        line = rfile.readline(_MAXLINE + 1)
        reqData += line
        header_lines.append(line)
        if line in ('\r\n', '\n', ''):
            break
    hstring = ''.join(header_lines)
    headers = email.parser.Parser().parsestr(hstring)
    length = headers.get("Content-Length")
    try:
        n_bytes = int(length)
    except (TypeError, ValueError):
        n_bytes = 0

    if n_bytes > 0:
        reqData += rfile.read(n_bytes)

    #get host from header
    host = headers.get("Host")
    if host:
        return (reqData, host)
    
    #get host host from url
    scheme_position = path.find("://")
    if scheme_position == -1:
        path = path
    else:
        path = path[scheme_position+3:]
    
    host = path.split('/')[0]
    return (reqData, host)


def parse_response(con: socket.socket):
    #to be done
    pass
    

if __name__ == "__main__":
    main()