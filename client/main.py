from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivy.lang import Builder

class MainWindow(Screen):

    def new_access(self):
        print("fffffff")





class Authorization(Screen):
        pass

class Register(Screen):
    pass



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
