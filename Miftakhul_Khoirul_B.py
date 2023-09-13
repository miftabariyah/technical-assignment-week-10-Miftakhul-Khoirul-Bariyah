import RPi.GPIO as GPIO
from time import sleep
import Adafruit_ADS1x15
import requests
from hx711 import HX711
from w1thermsensor import W1ThermSensor

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=5, pd_sck_pin=6)
hx.set_scale_ratio(10)  # Ganti scale_ratio dengan nilai kalibrasi Anda
hx.reset()

# Inisialisasi ADC ADS1115
adc = Adafruit_ADS1x15.ADS1115()

# Konfigurasi gain (penggandaan) untuk pembacaan ampere
GAIN = 1  # Misalnya, jika diperlukan penggandaan 4x, ganti nilai ini menjadi 4

# Token dan label perangkat Ubidots
TOKEN = "BBFF-5Zptd1EDpETX1AHjfN1kdhAeXC6fzQ"
DEVICE_LABEL = "mifta1"  # Ganti dengan label perangkat Anda di Ubidots

def get_hx_data():
    berat = hx.get_raw_data_mean()
    return berat

def get_ads_data():
    ampere = adc.read_adc(0, gain=GAIN)  # Membaca data ampere dari pin A0 pada ADC ADS1115
    return ampere

def get_suhu_data():
    sensor = W1ThermSensor()
    suhu = sensor.get_temperature()
    return suhu

def update_ubidots(berat, suhu, ampere):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    payload = {
        "sensor-berat": berat,
        "sensor-suhu": suhu,
        "sensor-ampere": ampere
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Data berhasil dikirim ke Ubidots")
    else:
        print("Gagal mengirim data ke Ubidots. Kode status:", response.status_code)

try:
    while True:
        berat = get_hx_data()
        suhu = get_suhu_data()
        ampere = get_ads_data()
        
        # Kirim data ke Ubidots
        update_ubidots(berat, suhu, ampere)
        
        sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Program terminated.")
