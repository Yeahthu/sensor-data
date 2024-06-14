
# coding: utf-8

# In[3]:


from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
from datetime import datetime

app = Flask(__name__)
data_list = []


temp_data = {}


MQTT_BROKER = "c195ef0f5f534d53b72397d524b180f3.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC_TEMPERATURE = "dht11/suhu"
MQTT_TOPIC_HUMIDITY = "dht11/kelembapan"
MQTT_USERNAME = "gurass"
MQTT_PASSWORD = "Kawai21_"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_TEMPERATURE)
    client.subscribe(MQTT_TOPIC_HUMIDITY)

def on_message(client, userdata, msg):
    global temp_data, data_list
    payload = msg.payload.decode()
    topic = msg.topic
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Received message '{payload}' on topic '{topic}'")
    
    if topic == MQTT_TOPIC_TEMPERATURE:
        temp_data['suhu'] = str(payload)
    elif topic == MQTT_TOPIC_HUMIDITY:
        temp_data['kelembapan'] = str(payload)
    
   
    if 'suhu' in temp_data and 'kelembapan' in temp_data:
        data = {
            'timestamp': timestamp,
            'suhu': temp_data['suhu'],
            'kelembapan': temp_data['kelembapan']
        }
        data_list.append(data)
        print(f"Appended data: {data}")
        temp_data = {} 

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

@app.route('/sensor/data', methods=['POST'])
def add_dummy_data():
    readings = request.json.get('readings')
    print(f"Received readings: {readings}")

    if not readings:
        return jsonify({"error": "Missing data"}), 400

    for reading in readings:
        temperature = reading.get('suhu')
        humidity = reading.get('kelembapan')
        timestamp = reading.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if temperature is None or humidity is None:
            return jsonify({"error": "Missing data in one of the readings"}), 400

        dummy_data = {
            "suhu": temperature,
            "kelembapan": humidity,
            "timestamp": timestamp
        }
        data_list.append(dummy_data)
        print(f"Appended data: {dummy_data}")

    print(f"Final data list: {data_list}")
    return jsonify({"message": "Data added successfully"}), 200

@app.route('/sensor/data', methods=['GET'])
def get_data():
    print(f"Data list on GET request: {data_list}")
    return jsonify(data_list), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



# In[ ]:




