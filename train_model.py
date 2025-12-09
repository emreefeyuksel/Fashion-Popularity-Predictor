import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.utils import class_weight
import numpy as np
import matplotlib.pyplot as plt
import os

# --- AYARLAR ---
DATA_DIR = 'dataset'
IMG_SIZE = (224, 224)
BATCH_SIZE = 8
EPOCHS = 30  # Epoch sayısını biraz artırabiliriz istersen ama şimdilik 10 kalsın
LEARNING_RATE = 1e-5

def build_model(num_classes):
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    # ResNet katmanlarını dondur (sadece son katmanları eğiteceğiz)
    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)  # Overfitting önlemek için
    predictions = Dense(1, activation='sigmoid')(x)  # Binary classification (0 veya 1)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer=Adam(learning_rate=LEARNING_RATE),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model


def train():
    # Veri Yükleyicileri (Data Augmentation ile)
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2
    )

    print("🚀 Veriler hazırlanıyor...")
    train_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        subset='training'
    )

    validation_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        subset='validation'
    )

    # --- KRİTİK DÜZELTME: Sınıf Ağırlıklarını Hesapla ---
    # Bu kısım modelin az olan veriye daha çok önem vermesini sağlar
    from sklearn.utils import class_weight
    class_weights = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_generator.classes),
        y=train_generator.classes
    )
    # Keras'ın istediği formata çevir (Dictionary formatı)
    train_class_weights = dict(enumerate(class_weights))
    print(f"⚖️ Sınıf Ağırlıkları: {train_class_weights}")
    # ---------------------------------------------------

    print("\n🧠 Model inşa ediliyor...")
    model = build_model(num_classes=1)

    print("\n🔥 Eğitim Başlıyor...")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        class_weight=train_class_weights  # Ağırlıkları buraya ekledik!
    )

    # Modeli Kaydet
    model.save('fashion_model.h5')
    print("\n✅ Model kaydedildi: fashion_model.h5")

    # Grafik Çiz (Opsiyonel, hata verirse program durmaz)
    try:
        plt.plot(history.history['accuracy'])
        plt.plot(history.history['val_accuracy'])
        plt.title('Model Doğruluğu')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper left')
        plt.savefig('training_result.png')  # Ekrana basmak yerine dosyaya kaydeder
        print("📊 Grafik 'training_result.png' olarak kaydedildi.")
    except Exception as e:
        print("Grafik çizilemedi ama sorun değil.")


if __name__ == "__main__":
    train()