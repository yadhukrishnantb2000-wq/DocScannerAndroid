
import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from PIL import Image

from plyer import filechooser, camera


class DocumentScanner(App):
    def build(self):
        self.pages = []

        root = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(10)
        )

        root.add_widget(Label(
            text="DOCUMENT SCANNER",
            font_size="24sp",
            bold=True,
            size_hint_y=None,
            height=dp(55)
        ))

        self.status = Label(
            text="Scan or import document images",
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(self.status)

        buttons = [
            ("Import Images", self.import_images),
            ("Scan with Camera", self.scan_camera),
            ("Create PDF", self.create_pdf),
            ("Clear Pages", self.clear_pages),
        ]

        for caption, action in buttons:
            btn = Button(
                text=caption,
                size_hint_y=None,
                height=dp(52)
            )
            btn.bind(on_release=action)
            root.add_widget(btn)

        scroll = ScrollView()
        self.page_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(5)
        )
        self.page_list.bind(
            minimum_height=self.page_list.setter("height")
        )
        scroll.add_widget(self.page_list)
        root.add_widget(scroll)

        return root

    def show_message(self, title, message):
        Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.88, 0.4)
        ).open()

    def add_page(self, path):
        try:
            path = os.path.abspath(path)

            with Image.open(path) as img:
                img.verify()

            if path not in self.pages:
                self.pages.append(path)
                self.page_list.add_widget(Label(
                    text=os.path.basename(path),
                    size_hint_y=None,
                    height=dp(35)
                ))

            self.status.text = (
                f"{len(self.pages)} page(s) selected"
            )
        except Exception as exc:
            self.show_message("Invalid image", str(exc))

    def import_images(self, *_):
        try:
            filechooser.open_file(
                on_selection=self.on_files_selected,
                filters=["*.jpg", "*.jpeg", "*.png", "*.webp"]
            )
        except Exception as exc:
            self.show_message("File picker error", str(exc))

    def on_files_selected(self, selection):
        for path in selection or []:
            self.add_page(path)

    def scan_camera(self, *_):
        output = os.path.join(
            self.user_data_dir,
            "scan_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".jpg"
        )

        try:
            camera.take_picture(
                filename=output,
                on_complete=self.on_camera_complete
            )
        except Exception as exc:
            self.show_message("Camera error", str(exc))

    def on_camera_complete(self, path):
        if path and os.path.isfile(path):
            self.add_page(path)
        else:
            self.status.text = "Camera capture cancelled"

    def create_pdf(self, *_):
        if not self.pages:
            self.show_message(
                "No pages",
                "Import or scan at least one image first."
            )
            return

        output_dir = os.path.join(
            self.user_data_dir, "Documents"
        )
        os.makedirs(output_dir, exist_ok=True)

        filename = "Document_" + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        ) + ".pdf"

        output = os.path.join(output_dir, filename)
        converted = []

        try:
            for path in self.pages:
                with Image.open(path) as img:
                    converted.append(img.convert("RGB"))

            first, rest = converted[0], converted[1:]
            first.save(
                output,
                "PDF",
                save_all=True,
                append_images=rest,
                resolution=150.0
            )

            self.status.text = "PDF created successfully"
            self.show_message(
                "PDF saved",
                "Saved to:\n" + output
            )

        except Exception as exc:
            self.show_message("PDF error", str(exc))

        finally:
            for img in converted:
                img.close()

    def clear_pages(self, *_):
        self.pages.clear()
        self.page_list.clear_widgets()
        self.status.text = "All selected pages cleared"


if __name__ == "__main__":
    DocumentScanner().run()
