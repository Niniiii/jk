# -*- coding: utf-8 -*-

import logging
import json
import requests

# 钉钉消息发送实现
def post(data):
    webhook_url='https://oapi.dingtalk.com/robot/send?access_token=${Token}' #钉钉群机器人的webhook的URL
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    post_data = json.dumps(data)
    try:
        response = requests.post(webhook_url, headers=headers, data=post_data)
        logging.info('Send success')
    except requests.exceptions.HTTPError as exc:
        logging.error("Send Error,HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
        raise
    except requests.exceptions.ConnectionError:
        logging.error("Send Error,HTTP connection error!")
        raise
    else:
        result = response.json()
        logging.info('Send Error:%s' % result)
        if result['errcode']:
            error_data = {"msgtype": "text", "text": {"content": "Send Error, reason:%s" % result['errmsg']}, "at": {"isAtAll": True}}
            logging.error("Send Error:%s" % error_data)
            requests.post(webhook_url, headers=headers, data=json.dumps(error_data))
        return result

# 发送钉钉markdown消息
def post_markdown(title,text):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text
        },
        "at": {
            "atMobiles": [],
            "isAtAll": False
        }
    }
    post(data)

# 函数计算入口
def handler(event, context):
    logger = logging.getLogger()
    evt = json.loads(event)
    #OSS endpoint url
    post_markdown('告警','![screenshot](https://${bucket}.oss-cn-hangzhou.aliyuncs.com/photo/%s)' % evt.get('photo',''))
    logger.info('photo name is %s', evt.get('photo',''))
    return 'OK'
