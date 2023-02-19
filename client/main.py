from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder

import threading
import socket

# Connect to server
class Connection_server():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', 5000))

    # Button register
    def server_msg(self, data):
        # Send message to sever
        self.client.sendall(bytes(' '.join(data) , "UTF-8"))
        # Wait message from the server
        revers_msg = self.client.recv(4096).decode("UTF-8")
        return revers_msg

class MainWindow(Screen):
    def update_data(self, data):
        data = ["Update", data]
        server = Connection_server()
        answer = server.server_msg(data)
        print(answer)


class Authorization(Screen):

    def login_btn(self, app):
        if (self.login.text != '' and self.password.text != ''):
            data = ["Login", self.login.text, self.password.text]
            server = Connection_server()
            answer = server.server_msg(data)
            if answer == "Done":
                update = MainWindow()
                update.update_data(data[1])
                app.root.current = "main_window"
            else:
                enter_data = MDDialog(text= answer)
                enter_data.open()
        else:
            enter_data = MDDialog(text="Enter the data!")
            enter_data.open()

class Register(Screen):

    def registration(self):

        if (self.username.text != '' and self.login.text != '' and self.password.text != ''):
            server = Connection_server()
            answer = server.server_msg(data = ["Register", self.username.text, self.login.text, self.password.text])
            enter_data = MDDialog(text= answer)
            enter_data.open()
        else:
            enter_data = MDDialog(text="Enter the data!")
            enter_data.open()


class WindowManager(ScreenManager):
    pass




class MyApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        kv = Builder.load_file('window.kv')
        return kv



if __name__ == '__main__':
    MyApp().run()
