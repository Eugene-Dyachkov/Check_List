from setings_sql import host, user, password, db_name
import pymysql

class DataBase():
    def first_connect(self):
        '''
        conect mySQL, create table
        '''
        try:
            self.connection = pymysql.connect(
                host=host,
                port=3306,
                user=user,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("connection complite!")
            try:
                # Create cursor
                self.cursor = self.connection.cursor()

                # Create table users
                self.cursor.execute("CREATE TABLE IF NOT EXISTS users(us_id int AUTO_INCREMENT,"\
                    "username varchar(32) NOT NULL,"\
                    "login varchar(32) NOT NULL,"\
                    "password varchar(32) NOT NULL,"\
                    "PRIMARY KEY(us_id));"
                    )

                # Create table projects
                self.cursor.execute("CREATE TABLE IF NOT EXISTS projects(pr_id int AUTO_INCREMENT,"\
                    "name varchar(32) NOT NULL,"\
                    "user_id int NOT NULL,"\
                    "FOREIGN KEY (user_id) REFERENCES users(us_id),"\
                    "PRIMARY KEY(pr_id));"
                    )

                # Create table notes
                self.cursor.execute("CREATE TABLE IF NOT EXISTS notes(no_id int AUTO_INCREMENT,"\
                    "headind varchar(32) NOT NULL,"\
                    "text varchar(150),"\
                    "project_id int NOT NULL,"\
                    "FOREIGN KEY (project_id) REFERENCES projects(pr_id),"\
                    "PRIMARY KEY(no_id));"
                    )
                print("Is complite!")
            finally:
                self.connection.close()

        except Exception as ax:
            print(ax)



import socket
from select import select

class Server():
    to_read = {}
    to_write = {}

    tasks = []

    def connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind(('localhost', 5000))
        self.server_socket.listen()

        while True:
            yield ('read', self.server_socket)
            client_socket, addr = self.server_socket.accept()
            print(f"New connection {addr}")

            self.tasks.append((self.client(client_socket)))

    def client(self, client_socket):
        while True:
            yield ('read', client_socket)
            request = client_socket.recv(4096)

            if not request:
                break
            else:

                yield ('write', client_socket)
                client_socket.send('Hello'.encode())
                msg = request.decode()
                print(msg)


        client_socket.close()

    def event_loop(self):

        while any([self.tasks, self.to_read, self.to_write]):

            while not self.tasks:
                ready_to_read, ready_to_write, _ = select(self.to_read, self.to_write, [])

                for sock in ready_to_read:
                    self.tasks.append(self.to_read.pop(sock))

                for sock in ready_to_write:
                    self.tasks.append(self.to_write.pop(sock))

            try:
                task = self.tasks.pop(0)

                reason, sock = next(task)

                if reason == 'read':
                    self.to_read[sock] = task
                if reason == 'write':
                    self.to_write[sock] = task

            except:
                print('Done')





if __name__ == "__main__":
    d = DataBase()
    d.first_connect()
    s = Server()
    s.tasks.append(s.connect())
    s.event_loop()
