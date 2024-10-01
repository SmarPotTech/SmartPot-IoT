from machine import ADC, Pin
from time import sleep, localtime
import network
import utelegram
from config import utelegram_config, wifi_config

# Importar clases de sensores desde sensors.py
from sensors import (
    LightSensor,
    PHSensor,
    TDSSensor,
    HumiditySoilSensor,
    AtmosphereSensor,
)

# Importar funciones desde utilitys.py
from utilitys import (
    print_table,
    send_msg
)

# Variable global para controlar si se debe enviar el mensaje
should_send_msg = False

if __name__ == "__main__":
    # Instancia de cada sensor digital
    dht_sensor = AtmosphereSensor(15)
    # Instancia de cada sensor ADC
    light_sensor = LightSensor(34)
    ph_sensor = PHSensor(35)
    tds_sensor = TDSSensor(32)
    humidity_soil_sensor = HumiditySoilSensor(33)

    # Configuración inicial de WiFi y pines
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(wifi_config['ssid'], wifi_config['password'])

    # Definir bot aquí
    bot = None

    # Espera activa hasta 20 segundos para conectar
    for _ in range(20):
        if sta_if.isconnected():
            print('WiFi Conectado')
            try:
                bot = utelegram.ubot(utelegram_config['token'])
                should_send_msg = True  # Cambia el estado de envío de mensajes
                print('Bot inicializado correctamente')
            except Exception as e:
                print(f"Error al inicializar el bot: {e}")
            break
        print('Conectando a WiFi...')
        sleep(1)
    else:
        print('No conectado - abortando')

    # Enviar datos de los sensores cada 60 segundos
    while True:
        # Leer valores de los sensores
        dht_data = dht_sensor.read_value()
        temp = dht_data["temperature"]
        humidity_air = dht_data["humidity"]
        light = light_sensor.read_light()
        ph = ph_sensor.read_ph()
        tds = tds_sensor.read_tds()
        humidity_soil = humidity_soil_sensor.read_soil_humidity()

        # Imprimir los valores en formato tabla
        print_table(temp, humidity_air, light, ph, tds, humidity_soil)

        # Enviar mensaje si el bot está conectado y la variable `should_send_msg` es True
        if should_send_msg and bot:
            send_msg(bot, utelegram_config['chat'], temp, humidity_air, light, ph, tds, humidity_soil)

        sleep(60)