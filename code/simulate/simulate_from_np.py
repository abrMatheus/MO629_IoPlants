'''
'''



import random
import time
import json
import sys
import numpy as np

from gen_measure import gen_complete

from paho.mqtt import client as mqtt_client


#TODO: configure username, password of a plant
username = ''
password = ''

if username=='' or password=='':
    print("ERROR: Please configure username and password")
    exit()


broker = 'mqtt.prod.konkerlabs.net'
port = 1883
parent_topic = f"data/{username}/pub"

inner_topics = ['temp', 'hum', 'soil', 'lum']

# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish_measures(client, data_array):

    for t,h,s,l in data_array:
        time.sleep(1)

        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[0]}'
        MQTT_MSG=json.dumps({"metric":  "Celsius","value": float(t)})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_t = result[0]
        if status_t != 0:
            print(f"Failed to send message to topic {topic}")

        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[1]}'
        MQTT_MSG=json.dumps({"metric":  "Percentage","value": float(h)})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_h = result[0]
        if status_h != 0:
            print(f"Failed to send message to topic {topic}")


        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[2]}'
        MQTT_MSG=json.dumps({"metric":  "Percentage","value": float(s)})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_s = result[0]
        if status_s != 0:
            print(f"Failed to send message to topic {topic}")

        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[3]}'
        MQTT_MSG=json.dumps({"metric":  "Index","value": float(l)})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_l = result[0]
        if status_l != 0:
            print(f"Failed to send message to topic {topic}")
        


def run(data_path):
    data = np.load(data_path)
    if data.shape[1]!=4:
        print("error! data should have 4 columns")
        exit()
    client = connect_mqtt()
    client.loop_start()
    # publish(client)
    publish_measures(client, data)
    client.loop_stop()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage simulate.py <data.npy>")
        print("<data.npy> is a Nx4 array, with the columns being temperature, hum., soil hum. and luminosity")
        exit()
    
    run(sys.argv[1])
