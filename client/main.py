from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarListItem
from kivymd.uix.button import MDFlatButton
from kivy.uix.boxlayout import BoxLayout
import socket
import pickle


user = []



class Connection_server():
    '''
    Connect to server, sending messages to the server.
    '''
    # Connect to server
    def __init__(self):
        # Create user socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', 5000))

    # Button register
    def server_msg(self, data):
        # Send message to sever and message splitting
        self.client.sendall(bytes('&'.join(data) , "UTF-8"))
        # Wait message from the server
        revers_msg = self.client.recv(4096).decode("UTF-8")
        return revers_msg

    def server_pickle(self, data):
        # Send message to sever and message splitting
        self.client.sendall(bytes('&'.join(data), "UTF-8"))
        # Wait message from the server
        user_data = self.client.recv(4096)
        # return unpacking pickle
        return pickle.loads(user_data)


class MainWindow(Screen):
    pass

class MyItem(TwoLineAvatarListItem):
    pass

class NewNotes(BoxLayout):
    pass


class Authorization(Screen):
    '''
    All operations in screen "Authorization"
    '''

    # Click button "Login"
    def login_btn(self, app):
        # Check for empty values
        if (self.login.text != '' and self.password.text != ''):
            data = ["Login", self.login.text, self.password.text]
            # Sending data
            answer = Connection_server().server_msg(data)
            # Answer check
            if answer == "Done":
                login = ["UserD", self.login.text]
                # Getting all user data
                user_data = Connection_server().server_pickle(login)
                global user
                user = [user_data[0]["us_id"], user_data[0]["username"], user_data[0]["login"]]
                # Opening a root window
                app.root.current = "main_window"
            else:
                # Create a message
                enter_data = MDDialog(
                    text= answer,
                    radius= [50, 7, 50, 7]
                )
                enter_data.open()
        else:
            # Create a message
            enter_data = MDDialog(
                text="Enter the data!",
                radius= [50, 7, 50, 7]
            )
            enter_data.open()

class Register(Screen):
    '''
    All operations in screen "Register"
    '''

    # Click button "Login"
    def registration(self):
        # Check for empty values
        if (self.username.text != '' and self.login.text != '' and self.password.text != ''):
            data = ["Register", self.username.text, self.login.text, self.password.text]
            # Sending data
            server = Connection_server()
            answer = server.server_msg(data)

            # Create a message
            enter_data = MDDialog(
                text= answer,
                radius= [50, 7, 50, 7]
            )
            enter_data.open()
        else:
            # Create a message
            enter_data = MDDialog(
                text="Enter the data!",
                radius= [50, 7, 50, 7]
            )
            enter_data.open()


class WindowManager(ScreenManager):
    '''
    All operations in screen "Root window"
    '''
    # All selection notes
    selection_notes = []
    # Filling screen "user"
    def set_user_data(self, *args):
        self.scr = self.screens[1].ids.username_label.text = user[1]
        self.scr = self.screens[1].ids.login_label.text = user[2]

    # Change tool bar on selection
    def set_selection_mode(self, instance_selection_list, mode):
        self.scr = self.screens[1].ids
        if mode:
            self.scr.toolbar.right_action_items = [["trash-can", lambda x: self.del_notes(x)]]
        else:
            self.scr.toolbar.right_action_items = [["plus", lambda x: self.add_new_note(x)]]
            self.scr.toolbar.left_action_items = [["update", lambda x: self.update(x)]]

    def on_selected(self, instance_selection_list, instance_selection_item):
        self.selection_notes.append(
            instance_selection_item.children[1].children[1]
        )

    def del_notes(self, x):
        '''
        Deleting a note
        '''
        # Creating a Send Message
        notes = ["DelNotes", str(user[0])]

        for note in self.selection_notes:
            notes.append(note.children[2].text)
        # Sending data
        server = Connection_server()
        answer = server.server_msg(notes)
        # Create a message
        enter_data = MDDialog(
            text= answer,
            radius= [50, 7, 50, 7]
        )
        self.update(x)
        enter_data.open()

    def update(self, x):
        '''
        Update a notes list
        '''
        # Creating a Send Message
        user_id = ["Update", str(user[0])]
        # Sending data
        notes = Connection_server().server_pickle(user_id)
        self.screens[1].ids.selection_list.clear_widgets()
        # Filling layout
        for item in notes:
            self.screens[1].ids.selection_list.add_widget(
                MyItem(
                    id = str(item['no_id']),
                    text = item['headind'],
                    secondary_text= item['text'],
                    size_hint_y=None,
                    on_touch_down=self.label_click
                )
            )

    def label_click(self, w, touch):
        # Click a note
        if w.collide_point(*touch.pos):
            # Double click check
            if touch.is_double_tap:
                full_note = MDDialog(
                    title = w.children[1].children[2].text,
                    text= w.children[1].children[1].text,
                    radius= [50, 7, 50, 7]
                )
                full_note.open()


    def add_new_note(self,x):
        '''Click a button "Plus"'''
        # Create a dialog
        self.new_note = MDDialog(
                    title = "New note",
                    type="custom",
                    content_cls=NewNotes(),
                    radius= [50, 7, 50, 7],
                    buttons=[
                    MDFlatButton(
                        text="OK",
                        #When you press
                        on_release= self.send_to_server
                    ),
                    ]
                )
        self.new_note.open()

    def send_to_server(self, inst):
        # Create send message
        add_note = Connection_server().server_msg(data=[
            "NewNotes",
            self.new_note.content_cls.children[1].text,
            self.new_note.content_cls.children[0].text,
            str(user[0])
            ])
        # Update list
        self.update(inst)
        # Clear text
        self.new_note.content_cls.children[1].text = ''
        self.new_note.content_cls.children[0].text = ''
        # Create a dialog
        enter_data = MDDialog(
                text=add_note,
                radius= [50, 7, 50, 7]
            )
        enter_data.open()


    def change_password(self):
        '''Click a button "Change password"'''
        new_pass = ["Password", str(user[0]), self.screens[1].ids.NewPass.text]
        # Send to server new password
        answer = Connection_server().server_msg(new_pass)
        # Create a dialog
        enter_data = MDDialog(
                text=answer,
                radius= [50, 7, 50, 7]
            )
        enter_data.open()

class MyApp(MDApp):
    def build(self):
        # Create App
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        kv = Builder.load_file('window.kv')
        return kv



if __name__ == '__main__':
    MyApp().run()
