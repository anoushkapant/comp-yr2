import socket
import threading
import datetime
import os
import mimetypes

#server setting
jls_extract_var = '127.0.0.1'
HOST =jls_extract_var
PORT = 8080

#creating a cache dictionary
cache={}

#creating the server socket
server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST,PORT))
server_socket.listen(5)

print(f"The server is running on {HOST}:{PORT}")

def client(client_socket,client_address):
    request= client_socket.recv(1024).decode('utf-8')
    print(f"Recieved a request from {client_address}:{request}")

    try:
        request_lines = request.split("\n")
        request_line = request_lines[0]
        headers = request_lines[1:]
        method, path, _ = request_line.split()

        #extracting User-agent
        user_agent = "Unknown"
        for header in headers:
            if header.startswith("User-Agent:"):
                user_agent = header.split(": ", 1)[1]
                break

        filename = path.lstrip("/")
        if filename == "":
            filename = "index.html"
        
        #response handling
        if method not in ["GET", "HEAD"]:
            response = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n<html><body><h1>400 Bad Request</h1></body></html>"
            status_code = "400 Bad Request"
        elif not os.path.exists(filename):
            response = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n<html><body><h1>404 Not Found</h1></body></html>"
            status_code = "404 Not Found"
        elif not os.access(filename, os.R_OK):
            response = "HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n<html><body><h1>403 Forbidden</h1></body></html>"
            status_code = "403 Forbidden"
        else:
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type is None:
                response = "HTTP/1.1 415 Unsupported Media Type\nContent-Type: text/html\n\n<html><body><h1>415 Unsupported Media Type</h1></body></html>"
                status_code = "415 Unsupported Media Type"
            else:
                last_modified = os.path.getmtime(filename)
                last_modified_time = datetime.datetime.utcfromtimestamp(last_modified).strftime("%a, %d %b %Y %H:%M:%S GMT")

                # Caching & Conditional GET
                if_modified_since = None
                for header in headers:
                    if header.startswith("If-Modified-Since:"):
                        if_modified_since = header.split(": ", 1)[1]
                        break

                if if_modified_since == last_modified_time:
                    response = "HTTP/1.1 304 Not Modified\nContent-Type: text/html\n\n"
                    status_code = "304 Not Modified"
                else:
                    with open(filename, "rb") as f:
                        content = f.read()

                    cache[filename] = {
                        "content": content,
                        "last_modified": last_modified
                    }
                    response_header = f"HTTP/1.1 200 OK\nContent-Type: {mime_type}\nLast-Modified: {last_modified_time}\n"

                    response = response_header + "\n" + (content.decode("utf-8") if method == "GET" else "")
                    status_code = "200 OK"

    except Exception:
        response = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n<html><body><h1>400 Bad Request</h1></body></html>"
        status_code = "400 Bad Request"

    #logging the client request & response
    log_entry = f"{client_address[0]} | {datetime.datetime.now()} | {method} {filename} | {status_code} | {user_agent}\n"
    with open("server_log.txt", "a") as log_file:
        log_file.write(log_entry)

    #to send response
    client_socket.sendall(response.encode("utf-8"))

    #to handle persistent connections
    connection_close = any(header.lower().startswith("connection: close") for header in headers)
    if connection_close:
        client_socket.close()

#threading to accept more clients
while True:
    client_sock, client_addr = server_socket.accept()
    client_thread = threading.Thread(target=client, args=(client_sock, client_addr))
    client_thread.start()
