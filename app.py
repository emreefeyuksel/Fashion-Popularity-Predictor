import tkinter as tk
from tkinter import filedialog, Label, Frame
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np
import os

# --- AYARLAR ---
MODEL_PATH = 'fashion_model.h5'
IMG_SIZE = (224, 224)

class TrendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Moda Trend Tahmincisi")
        self.root.geometry("500x650")
        self.root.configure(bg="#f0f0f0")

        # Başlık
        self.header = tk.Label(root, text="Kıyafet Popülarite Analizi",
                               font=("Helvetica", 18, "bold"), bg="#f0f0f0", fg="#333")
        self.header.pack(pady=20)

        # Model Yükleme Durumu
        self.status_label = tk.Label(root, text="Model Yükleniyor...", fg="orange", bg="#f0f0f0")
        self.status_label.pack()

        # Resim Alanı (Başlangıçta boş)
        self.image_frame = Frame(root, bg="white", width=300, height=300, relief="sunken", bd=2)
        self.image_frame.pack(pady=20)
        self.image_frame.pack_propagate(False) # Boyutu sabitle

        self.panel = Label(self.image_frame, bg="white", text="Resim Yok")
        self.panel.pack(expand=True)

        # Sonuç Alanı
        self.result_label = tk.Label(root, text="Tahmin Bekleniyor...",
                                     font=("Helvetica", 14), bg="#f0f0f0", fg="#666")
        self.result_label.pack(pady=10)

        # Buton
        self.btn = tk.Button(root, text="Fotoğraf Yükle ve Analiz Et",
                             command=self.upload_image,
                             font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                             padx=20, pady=10, relief="flat", cursor="hand2")
        self.btn.pack(pady=20)

        # Modeli Başlat
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = tf.keras.models.load_model(MODEL_PATH)
                self.status_label.config(text="✅ Model Hazır", fg="green")
            except Exception as e:
                self.status_label.config(text=f"Hata: {str(e)}", fg="red")
        else:
            self.status_label.config(text="❌ Model Dosyası Bulunamadı!", fg="red")
            self.btn.config(state="disabled")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return

        # 1. Resmi Arayüzde Göster
        img_display = Image.open(file_path)
        img_display = img_display.resize((300, 300), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_display)
        self.panel.configure(image=img_tk, text="")
        self.panel.image = img_tk

        # 2. Tahmin Yap
        self.predict(file_path)

    def predict(self, file_path):
        self.result_label.config(text="Analiz ediliyor...", fg="blue")
        self.root.update()

        # Resmi modele uygun hale getir
        img = tf.keras.preprocessing.image.load_img(file_path, target_size=IMG_SIZE)
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        # Model tahmini
        prediction = self.model.predict(img_array)
        score = prediction[0][0]

        # Sonucu yazdır
        if score > 0.5:
            text = f"🔥 POPÜLER! (Güven: %{score*100:.1f})"
            color = "#D32F2F" # Kırmızı
        else:
            text = f"❄️ Popüler Değil (Güven: %{(1-score)*100:.1f})"
            color = "#1976D2" # Mavi

        self.result_label.config(text=text, fg=color, font=("Helvetica", 16, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = TrendApp(root)
    root.mainloop()