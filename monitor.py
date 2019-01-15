# -*- coding: utf-8 -*-

import json
import uuid
import logging
from time import sleep
from picamera import PiCamera
import RPi.GPIO as GPIO
import oss2
import aliyunsdkiotclient.AliyunIotMqttClient as iot

# 参数定义
options = {
    'productKey': '${a1KVGJcmmvj}',  # 设备标识三元组
    'deviceName': '${device_test}',  # 设备标识三元组
    'deviceSecret': '${1SFDI5DPtvldVBdhgJ2Qp8rP1PSAhn2k}',  # 设备标识三元组
    'port': 1883,  # iot mqtt port
    'host': 'iot-as-mqtt.cn-shanghai.aliyuncs.com',  # iot mqtt endpoint
    'endpoint': 'http://oss-cn-hangzhou.aliyuncs.com',  # oss endpoint
    'ak': '${ak}',
    'sk': '${sk}',
    'bucket': '${bucket}',  # oss bucket
    'ir_pin': 24  # 人体红外感应器设置读取针脚标号
}

topic = '/' + options['productKey'] + '/' + options['deviceName'] + '/user/test'

# 拍照存oss，并发送通知
def takephoto2oss(client):

    #拍照
    photo_filename = str(uuid.uuid1()) + ".jpg"
    print('take photo :' + photo_filename)
    camera.capture('photo/' + photo_filename)

    #存OSS
    print('save photo to oss :' + photo_filename)
    bucket.put_object_from_file(
        'photo/' + photo_filename, 'photo/' + photo_filename)

    #消息上送
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
    # GPIO 初始化
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(options['ir_pin'], GPIO.IN)

    # 摄像头 初始化
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.vflip = True
    camera.hflip = True

    # OSS 初始化
    auth = oss2.Auth(options['ak'], options['sk'])
    bucket = oss2.Bucket(auth, options['endpoint'], options['bucket'])

    # IOT Mqtt 初始化
    client = iot.getAliyunIotMqttClient(options['productKey'], options['deviceName'], options['deviceSecret'], secure_mode = 3)
    client.on_connect = on_connect
    client.connect(host=options['productKey'] + '.' + options['host'], port=options['port'], keepalive = 60)

    while True:
        # 当高电平信号输入时报警
        if GPIO.input(options['ir_pin']) == True:
            print " Someone is coming!"
            takephoto2oss(client)
        else:
            continue
        sleep(3)
