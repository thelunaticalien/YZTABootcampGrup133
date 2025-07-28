"""
MoonLightDrive – Yapay Zeka Destekli Duygu Analiz Programı
MoonLightDrive- Gecenin karanlığında sizi Ay Işığının Sürüşüyle ışığa ulaştıracağız.
Projede PyQT5 uygulaması kullanılarak günlük metinleri analiz eden ve duygusal geri bildirim sağlayan bir programdır.

Kodu Okuyana Notlar:
- .env dosyasında MISTRAL_API_KEY tanımlanmalıdır. Gizlilik gereği API Key kısmı size bırakılmıştır.
- Openrouter sitesinden ücretsiz API alabilirsiniz.
- Mistral API (ücretsiz sürüm) ile entegre edilmiştir.
- Yapay Zekanın Türkçeyle sorunları olmasından bazı yerlerde Türkçe'ye zorlanmıştır.
- Temiz Kod prensipleri gereği değişken isimleri ayarlanmıştır.


"""

import sys
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QTextEdit, QPushButton, QTabWidget, QMessageBox, QListWidget
)


# Env Verilerini Yükle
load_dotenv()

# API Ayarları
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_ID = "mistralai/mistral-7b-instruct:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
LOG_FILE = "logs.json"

# Mistral API Analizi
def analyze_with_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"[API Hatası] {response.status_code}: {response.text}")

# Logları Kaydet
def save_log(entry):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# Logları Yükle
def load_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# Uygulama Dosyası
class MoonLightDriveApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoonLightDrive – PyQt5")
        self.setGeometry(300, 100, 500, 550)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_daily_tab()
        self.init_history_tab()
        self.init_general_advice_tab()

    def init_daily_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.journal_input = QTextEdit()
        self.analyze_button = QPushButton("Duygusal Analiz Et")

        self.result_label = QLabel("Analiz sonucu burada görünecek.")
        self.result_label.setWordWrap(True)
        self.result_label.setMaximumWidth(460)

        self.analyze_button.clicked.connect(self.analyze_entry)

        layout.addWidget(QLabel("Bugünkü düşüncelerini yaz:"))
        layout.addWidget(self.journal_input)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.result_label)
        tab.setLayout(layout)

        self.tabs.addTab(tab, "Günlük")

    def init_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.history_list = QListWidget()

        layout.addWidget(QLabel("Geçmiş Günlükler:"))
        layout.addWidget(self.history_list)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Geçmiş")

        self.load_history()

    def init_general_advice_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.general_advice_label = QLabel("Öneri yükleniyor...")
        self.general_advice_label.setWordWrap(True)
        self.general_advice_label.setMaximumWidth(460)

        self.refresh_advice_button = QPushButton("Güncelle")
        self.refresh_advice_button.clicked.connect(self.generate_general_advice)

        layout.addWidget(QLabel("Genel Ruh Hali Tavsiyesi:"))
        layout.addWidget(self.general_advice_label)
        layout.addWidget(self.refresh_advice_button)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Genel Tavsiye")
        self.generate_general_advice()

    def analyze_entry(self):
        text = self.journal_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir şeyler yaz.")
            return
        try:
            prompt = (
                "Aşağıdaki metni duygusal olarak değerlendirir misin? Cevabını Türkçe olarak, empatik bir dille yaz lütfen."
                "Mutlaka TÜRKÇE yanıt ver. Anlamlı, empatik ve duygusal bir analiz yap:\n\n" + text
            )
            analysis = analyze_with_mistral(prompt)
            self.result_label.setText(analysis)

            entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": text,
                "analysis": analysis
            }
            save_log(entry)
            self.history_list.addItem(f"{entry['date']} - {analysis[:50]}...")

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def load_history(self):
        logs = load_logs()
        for log in logs:
            if isinstance(log, dict) and 'date' in log and 'analysis' in log:
                self.history_list.addItem(f"{log['date']} - {log['analysis'][:50]}...")

    def generate_general_advice(self):
        try:
            logs = load_logs()
            recent_logs = [log for log in logs if isinstance(log, dict) and 'text' in log]
            if not recent_logs:
                self.general_advice_label.setText("Yeterli veri yok.")
                return
            combined = "\n".join(log["text"] for log in recent_logs[-5:])
            prompt = (
                "Aşağıdaki günlük yazılarına göre bu kişinin ruh hali hakkında kısa ama anlamlı bir analiz yap "
                "Ona uygun öneriler ver. Cevabını mutlaka TÜRKÇE olarak ver:\n\n" + combined
            )
            advice = analyze_with_mistral(prompt)
            self.general_advice_label.setText(advice)
        except Exception as e:
            self.general_advice_label.setText(f"Hata: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoonLightDriveApp()
    window.show()
    sys.exit(app.exec_())
