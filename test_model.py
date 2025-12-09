import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# --- AYARLAR ---
MODEL_PATH = 'fashion_model.h5'
IMG_SIZE = (224, 224)


def predict_popularity(image_path):
    # 1. Modeli Yükle
    if not os.path.exists(MODEL_PATH):
        print("HATA: Model dosyası bulunamadı! Önce eğitimi tamamlayın.")
        return

    print(f"🧠 Model yükleniyor: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)

    # 2. Resmi Hazırla
    print(f"🖼️ Resim işleniyor: {image_path}")
    img = image.load_img(image_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Tek bir resim olduğu için boyut ekle
    img_array /= 255.0  # Normalizasyon (0-1 arası)

    # 3. Tahmin Yap
    prediction = model.predict(img_array)
    score = prediction[0][0]  # 0 ile 1 arası bir sayı döner

    print("\n--- SONUÇ ---")
    print(f"Ham Skor: {score:.4f}")

    # 0.5 eşik değerimizdir. 0.5 üstü Popüler, altı Değil.
    if score > 0.5:
        print(f"✅ TAHMİN: POPÜLER! (Güven: %{score * 100:.2f})")
    else:
        print(f"❌ TAHMİN: Popüler Değil. (Güven: %{(1 - score) * 100:.2f})")


if __name__ == "__main__":
    # BURAYA TEST ETMEK İSTEDİĞİN RESMİN ADINI YAZ
    # Resmi proje klasörünün içine atmayı unutma!
    resim_adi = "test_elbise.jpg"

    if os.path.exists(resim_adi):
        predict_popularity(resim_adi)
    else:
        print(f"Lütfen '{resim_adi}' adında bir resmi proje klasörüne koyun.")