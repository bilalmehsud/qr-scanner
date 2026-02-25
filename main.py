import sqlite3
import webbrowser
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import TwoLineListItem
from PIL import Image

try:
    from pyzbar.pyzbar import decode
except ImportError:
    decode = None

# Request Android permissions based on platform
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.CAMERA,
        Permission.INTERNET
    ])

KV = '''
MDScreenManager:
    MDScreen:
        name: "main"
        MDBottomNavigation:
            # Scanner Tab
            MDBottomNavigationItem:
                name: 'scan'
                text: 'Scanner'
                icon: 'qrcode-scan'

                FloatLayout:
                    Camera:
                        id: camera
                        resolution: (640, 480)
                        play: True
                        allow_stretch: True
                        keep_ratio: True
                        size_hint: 1, 1

                    # Overlay Box
                    Widget:
                        size_hint: None, None
                        size: dp(250), dp(250)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        canvas.after:
                            Color:
                                rgba: 0, 1, 0, 1
                            Line:
                                rectangle: self.x, self.y, self.width, self.height
                                width: dp(2)

            # History Tab
            MDBottomNavigationItem:
                name: 'history'
                text: 'History'
                icon: 'history'
                on_tab_press: app.load_history()

                MDScrollView:
                    MDList:
                        id: history_list
'''

class QRCodeScannerApp(MDApp):
    dialog = None
    scanning_active = True

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        self.init_db()
        return Builder.load_string(KV)

    def on_start(self):
        self.camera = self.root.get_screen("main").ids.camera
        Clock.schedule_interval(self.analyze_frame, 1.0 / 10.0) # Run 10 times a second

    def init_db(self):
        self.conn = sqlite3.connect("history.db")
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def analyze_frame(self, dt):
        if not self.scanning_active or not self.camera.texture or decode is None:
            return

        texture = self.camera.texture
        size = texture.size
        pixels = texture.pixels

        try:
            # Convert texture to a PIL Image format readable by PyZbar
            pil_image = Image.frombytes(mode='RGBA', size=size, data=pixels)
            barcodes = decode(pil_image)
            
            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8')
                self.scanning_active = False
                self.save_to_db(barcode_data)
                self.show_dialog(barcode_data)
        except Exception as e:
            print("Decoding error:", e)

    def save_to_db(self, data):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO scans (data) VALUES (?)", (data,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass # Ignore duplicate inserts

    def show_dialog(self, decoded_text):
        if not self.dialog:
            self.dialog = MDDialog(
                title="QR Code Detected!",
                text=decoded_text,
                buttons=[
                    MDFlatButton(
                        text="DISMISS",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog,
                    ),
                    MDFlatButton(
                        text="OPEN LINK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.open_link(self.dialog.text),
                    ),
                ],
            )
        else:
            self.dialog.text = decoded_text
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()
        self.scanning_active = True

    def open_link(self, link):
        self.dialog.dismiss()
        self.scanning_active = True
        try:
            webbrowser.open(link)
        except Exception:
            pass

    def load_history(self):
        history_list = self.root.get_screen("main").ids.history_list
        history_list.clear_widgets()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT data, timestamp FROM scans ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        for row in rows:
            history_list.add_widget(
                TwoLineListItem(text=row[0], secondary_text=str(row[1]))
            )

if __name__ == '__main__':
    QRCodeScannerApp().run()
