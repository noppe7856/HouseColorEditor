import customtkinter as ctk
import cv2
import numpy as np
import logging
from tkinter import filedialog
from PIL import Image, ImageTk

def imread_unicode(file_path):
    with open(file_path, "rb") as f:
        file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img

class ColorReplaceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("色置換ツール")
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.geometry("800x600")

        self.canvas = ctk.CTkCanvas(self, width=500, height=400, bg="gray")
        self.canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.load_button = ctk.CTkButton(self, text="画像を開く", command=self.load_image)
        self.load_button.grid(row=1, column=0, padx=10, pady=10)

        self.replace_button = ctk.CTkButton(self, text="色を置換", command=self.replace_color, state="disabled")
        self.replace_button.grid(row=1, column=2, padx=10, pady=10)

        self.color_picker_button = ctk.CTkButton(self, text="置換色を選択", command=self.pick_color)
        self.color_picker_button.grid(row=1, column=1, padx=10, pady=10)

        self.color_label = ctk.CTkLabel(self, text="選択された色:")
        self.color_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.color_display = ctk.CTkFrame(self, width=50, height=30, fg_color="white")
        self.color_display.grid(row=2, column=1, padx=10, pady=10)

        self.selected_color = None
        self.tolerance = 30

        self.image = None
        self.tk_image = None
        self.image_path = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("画像ファイル", "*.jpg;*.png;*.jpeg")])
        if not file_path:
            return

        self.image_path = file_path
        # imread_unicodeを利用して画像を読み込み
        self.image = imread_unicode(file_path)
        if self.image is None:
            logging.error("画像の読み込みに失敗しました。パスやファイルの整合性を確認してください。")
            return

        self.display_image()
        self.canvas.bind("<Button-1>", self.get_color)
        self.replace_button.configure(state="normal")

    def display_image(self):
        if self.image is None:
            return

        image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        aspect_ratio = self.image.shape[1] / self.image.shape[0]
        new_width = 500
        new_height = int(new_width / aspect_ratio)
        if new_height > 400:
            new_height = 400
            new_width = int(new_height * aspect_ratio)
        pil_image = pil_image.resize((new_width, new_height))
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def get_color(self, event):
        if self.image is None:
            return

        x_ratio = self.image.shape[1] / 500
        y_ratio = self.image.shape[0] / 400
        x = int(event.x * x_ratio)
        y = int(event.y * y_ratio)

        self.selected_color = self.image[y, x].copy()
        logging.info("選択された色: %s", self.selected_color)

        b, g, r = self.selected_color
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_display.configure(fg_color=hex_color)

    def replace_color(self):
        if self.image is None or self.selected_color is None:
            return

        self.new_color = np.array([255, 0, 0], dtype=np.uint8)
        # 色を置換するロジックをここに追加
        mask = cv2.inRange(self.image, self.selected_color - self.tolerance, self.selected_color + self.tolerance)
        self.image[mask != 0] = self.new_color
        self.display_image()

    def pick_color(self):
        color = ctk.CTkColorPicker()
        self.new_color = np.array(color, dtype=np.uint8)
        hex_color = f"#{self.new_color[2]:02x}{self.new_color[1]:02x}{self.new_color[0]:02x}"
        self.color_display.configure(fg_color=hex_color)

if __name__ == "__main__":
    app = ColorReplaceApp()
    app.mainloop()
