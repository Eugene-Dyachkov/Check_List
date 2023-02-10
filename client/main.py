from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivy.lang import Builder


import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5000))
client.sendall(bytes("XUN", "UTF-8"))



class MainWindow(Screen):

    def new_access(self):
        print("fffffff")





class Authorization(Screen):
        pass

class Register(Screen):
    def registration(self):
        global client
        client.sendall(bytes("Registration", "UTF-8"))



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
