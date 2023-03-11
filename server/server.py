
import pymysql
import threading
import pickle
import os

class DataBase():

    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host=os.getenv('host'),
                port=os.getenv('port'),
                user=os.getenv('user'),
                password=os.getenv('password'),
                database=os.getenv('database'),
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as ax:
            print(ax)

    def first_connect(self):
        '''
        conect mySQL, create table
        '''
        print("connection complite!")
        try:
            # Create cursor
            self.cursor = self.connection.cursor()

            # Create table users
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users(us_id int AUTO_INCREMENT,"\
                "username varchar(32) NOT NULL,"\
                "login varchar(32) NOT NULL UNIQUE,"\
                "password varchar(32) NOT NULL,"\
                "PRIMARY KEY(us_id));"
                )

            # Create table notes
            self.cursor.execute("CREATE TABLE IF NOT EXISTS notes(no_id int AUTO_INCREMENT,"\
                "headind varchar(32) NOT NULL,"\
                "text varchar(150),"\
                "user_id int NOT NULL,"\
                "FOREIGN KEY (user_id) REFERENCES users(us_id),"\
                "PRIMARY KEY(no_id));"
                )
            print("Is complite!")
        except:
            pass

    def registration(self, msg):
        '''Add new user'''
        try:
            self.cursor = self.connection.cursor() # Create cursor
            try:
                self.cursor.execute (f''' INSERT INTO users
                    (username, login, password)
                    VALUES('{msg[1]}','{msg[2]}','{msg[3]}');''')

                self.connection.commit()
                return "You signed up!"

            except pymysql.err.IntegrityError:
                return "Login busy, please try another one."

        except Exception as ex:
            print(ex)
            return "Error, try later!"

    def login_in(self, msg):
        '''Login user'''
        try:
            self.cursor = self.connection.cursor() # Create cursor
            try:
                self.cursor.execute(f''' SELECT login AS password FROM users WHERE login = "{msg[1]}" AND password = "{msg[2]}"''')
                result =[]
                result = self.cursor.fetchall()
                print(result)
                if result != ():
                    return "Done"
                else:
                    return "Incorrect login or password!"
            except Exception:
                return "Error, try later!"
        except Exception:
            return "Error, try later!"

    def user_data(self, msg):
        try:
            self.cursor = self.connection.cursor() # Create cursor
            try:
                self.cursor.execute(f''' SELECT us_id, username, login FROM users WHERE login = "{msg[1]}"''')
                data=pickle.dumps(self.cursor.fetchall())
                return data
            except Exception:
                return "Error, try later!"
        except Exception:
            return "Error, try later!"

    def new_notes(self, msg):
        try:
            self.cursor = self.connection.cursor() # Create cursor
            try:
                self.cursor.execute (f''' INSERT INTO notes
                    (headind, text, user_id)
                    VALUES('{msg[1]}','{msg[2]}','{msg[3]}');''')

                self.connection.commit()
                return "Note added!"

            except pymysql.err.IntegrityError:
                return "Error, try later!"

        except Exception as ex:
            return "Error, try later!"

    def update(self, msg):
        try:
            self.cursor = self.connection.cursor() # Create cursor
            try:
                # INSERT INTO users (headind, text, user_id) VALUES('111','222','333');
                self.cursor.execute(f''' SELECT no_id, headind, text FROM notes WHERE user_id = "{msg[1]}"''')
                data=pickle.dumps(self.cursor.fetchall())
                return data
            except Exception:
                return "Error, try later!"
        except Exception:
            return "Error, try later!"

    def DelNotes(self, msg):
        try:
            self.cursor = self.connection.cursor() # Create cursor
            for note in msg:
                print(note)
                if note != msg[0] and note != msg[1]:
                    self.cursor.execute (f'''DELETE FROM notes WHERE headind = "{note}" AND user_id = {msg[1]};''')
                    self.connection.commit()
            return "Delete!"
        except Exception:
                return "Error, try later!"

    def change_password(self, msg):
        try:
            print(msg)
            self.cursor = self.connection.cursor() # Create cursor
            try:
                self.cursor.execute (f'''UPDATE users SET password = "{msg[2]}" WHERE us_id = {int(msg[1])};''')

                self.connection.commit()

                return "You change password!"
            except Exception as ex:
                print(ex)

        except Exception:
                return "Error, try later!"



import threading
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
                msg = request.decode()
                msg = (msg.split('&'))
                thread = threading.Thread(target= self.msg_process, args=(client_socket, msg))
                thread.start()


        client_socket.close()


    def msg_process(self, client_socket, msg):
        data = DataBase()
        if msg[0] == "Register":
            client_socket.send(data.registration(msg).encode("UTF-8"))
        elif msg[0] == "Login":
            client_socket.send(data.login_in(msg).encode("UTF-8"))
        elif msg[0] == "Update":
            client_socket.send(data.update(msg))
        elif msg[0] == "NewNotes":
            client_socket.send(data.new_notes(msg).encode("UTF-8"))
        elif msg[0] == "UserD":
            client_socket.send(data.user_data(msg))
        elif msg[0] == "DelNotes":
            client_socket.send(data.DelNotes(msg).encode("UTF-8"))
        elif msg[0] == "Password":
            client_socket.send(data.change_password(msg).encode("UTF-8"))


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
