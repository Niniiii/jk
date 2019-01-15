# -*- coding: utf-8 -*-

import json
import uuid
import logging
from time import sleep
from picamera import PiCamera
import RPi.GPIO as GPIO
import oss2
import aliyunsdkiotclient.AliyunIotMqttClient as iot

# ��������
options = {
    'productKey': '${a1KVGJcmmvj}',  # �豸��ʶ��Ԫ��
    'deviceName': '${device_test}',  # �豸��ʶ��Ԫ��
    'deviceSecret': '${1SFDI5DPtvldVBdhgJ2Qp8rP1PSAhn2k}',  # �豸��ʶ��Ԫ��
    'port': 1883,  # iot mqtt port
    'host': 'iot-as-mqtt.cn-shanghai.aliyuncs.com',  # iot mqtt endpoint
    'endpoint': 'http://oss-cn-hangzhou.aliyuncs.com',  # oss endpoint
    'ak': '${ak}',
    'sk': '${sk}',
    'bucket': '${bucket}',  # oss bucket
    'ir_pin': 24  # ��������Ӧ�����ö�ȡ��ű��
}

topic = '/' + options['productKey'] + '/' + options['deviceName'] + '/user/test'

# ���մ�oss��������֪ͨ
def takephoto2oss(client):

    #����
    photo_filename = str(uuid.uuid1()) + ".jpg"
    print('take photo :' + photo_filename)
    camera.capture('photo/' + photo_filename)

    #��OSS
    print('save photo to oss :' + photo_filename)
    bucket.put_object_from_file(
        'photo/' + photo_filename, 'photo/' + photo_filename)

    #��Ϣ����
    payload_json = {
        'photo': photo_filename
    }
    print('send data to iot server: ' + str(payload_json))
    client.publish(topic, payload = str(payload_json))


def on_connect(client, userdata, flags_dict, rc):
    print("Connected with result code " + str(rc))


def on_disconnect(client, userdata, flags_dict, rc):
    print("Disconnected.")


if __name__ == '__main__':
    # GPIO ��ʼ��
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(options['ir_pin'], GPIO.IN)

    # ����ͷ ��ʼ��
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.vflip = True
    camera.hflip = True

    # OSS ��ʼ��
    auth = oss2.Auth(options['ak'], options['sk'])
    bucket = oss2.Bucket(auth, options['endpoint'], options['bucket'])

    # IOT Mqtt ��ʼ��
    client = iot.getAliyunIotMqttClient(options['productKey'], options['deviceName'], options['deviceSecret'], secure_mode = 3)
    client.on_connect = on_connect
    client.connect(host=options['productKey'] + '.' + options['host'], port=options['port'], keepalive = 60)

    while True:
        # ���ߵ�ƽ�ź�����ʱ����
        if GPIO.input(options['ir_pin']) == True:
            print " Someone is coming!"
            takephoto2oss(client)
        else:
            continue
        sleep(3)
