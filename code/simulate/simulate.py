'''

Code that simulates a plant measure for konkerlabs

configure username and password


usage of normal case:

simulage.py 0 0 0 0 


to simulate a abnormal case use 1 or 2:

simulate.py 0 0 0 1

this example will simulate a high abnormal case for luminosity

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



def normal_to_int(normal):
    new = []

    for n in normal:
        new.append(int(n))

    return new


def publish_measures(client, normal):
    t1,h1,s1,l1 = gen_complete(normal=normal)

    msg_count=0

    msg_len = len(t1)

    while True:
        time.sleep(1)

        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[0]}'
        MQTT_MSG=json.dumps({"metric":  "Celsius","value": t1[msg_count]})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_t = result[0]
        if status_t != 0:
            print(f"Failed to send message to topic {topic}")

        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[1]}'
        MQTT_MSG=json.dumps({"metric":  "Percentage","value": h1[msg_count]})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_h = result[0]
        if status_h != 0:
            print(f"Failed to send message to topic {topic}")


        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[2]}'
        MQTT_MSG=json.dumps({"metric":  "Percentage","value": s1[msg_count]})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_s = result[0]
        if status_s != 0:
            print(f"Failed to send message to topic {topic}")

        ##############################################################################
        topic = f'{parent_topic}/{inner_topics[3]}'
        MQTT_MSG=json.dumps({"metric":  "Index","value": l1[msg_count]})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status_l = result[0]
        if status_l != 0:
            print(f"Failed to send message to topic {topic}")
        


        msg_count += 1
        if msg_count >= msg_len-1:
            break

def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        MQTT_MSG=json.dumps({"deviceId": "My_favorite_thermometer",
                            "metric":  "Celsius","value": 27.0})
        result = client.publish(topic, MQTT_MSG)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 5:
            break


def run(normal):
    client = connect_mqtt()
    client.loop_start()
    # publish(client)
    publish_measures(client, normal_to_int(normal))
    client.loop_stop()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage simulate.py [1] [2] [3] [4]")
        print("[1] - 0 for normal temperature, 1 for high, 2 for low")
        print("[2] - 0 for normal humidity, 1 for high, 2 for low")
        print("[3] - 0 for normal soil humidity, 1 for high, 2 for low")
        print("[4] - 0 for normal luminosity, 1 for high, 2 for low")
        exit()
    
    run(sys.argv[1:])
