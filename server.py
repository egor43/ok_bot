from flask import Flask
from flask import request

import base64
import urllib
import json
import requests

app = Flask(__name__)

# Group's token
token = 'tkn149Nfu7Sl6rRLzzjW39xgayDFEOkXRGu6cAg2LMLbFAQTvl4Qey4jp9gJnurfzdaPz:CBAMCNMMEBABABABA'
# Last chat's identifier
last_chat_id = None

@app.route('/', methods=['POST'])
def entry():
    global last_chat_id
    new_message = request.data.decode()
    message_data = json.loads(new_message)
    last_chat_id = message_data['recipient']['chat_id']
    print(message_data)
    return 'Ok'

@app.route('/setwebhook/<webhook_address>', methods=['GET'])
def set_webhook(webhook_address):
    if not webhook_address:
        return "Error! No webhook address."
    webhook_address_b64 = urllib.parse.unquote(webhook_address)
    webhook_url = base64.b64decode(webhook_address_b64).decode()
    data = {'url': webhook_url}
    header = {'Content-Type': 'application/json;charset=utf-8'}
    request_address = 'https://api.ok.ru/graph/me/subscribe?access_token={token}'.format(token=token)
    response = requests.post(request_address, data=json.dumps(data), headers=header)
    return response.text

@app.route('/getwebhook', methods=['GET'])
def get_webhook():
    header = {'Content-Type': 'application/json;charset=utf-8'}
    request_address = 'https://api.ok.ru/graph/me/subscriptions?access_token={token}'.format(token=token)
    response = requests.get(request_address, headers=header)
    return response.text

@app.route('/removewebhook', methods=['GET'])
def remove_webhook():
    result = {}
    # Get installed webhooks
    webhooks = get_webhook()
    json_data = json.loads(webhooks)
    subscriptions = json_data['subscriptions']

    # Remove webhooks
    for subscription in subscriptions:
        data = {'url': subscription['url']}
        header = {'Content-Type': 'application/json;charset=utf-8'}
        request_address = 'https://api.ok.ru/graph/me/unsubscribe?access_token={token}'.format(token=token)
        response = requests.post(request_address, data=json.dumps(data), headers=header)
        result[subscription['url']] = response.text
    return str(result)

@app.route('/sendmessage/<message>', methods=['GET'])
def send_message(message):
    if not message:
        return "Error! No message."
    if not last_chat_id:
        return "Error! No last chat identifier."
    data = {'recipient': {'chat_id': last_chat_id}, 'message': {'text': message}}
    header = {'Content-Type': 'application/json;charset=utf-8'}
    request_address = 'https://api.ok.ru/graph/me/messages/{chat}?access_token={token}'.format(chat=last_chat_id, token=token)
    response = requests.post(request_address, data=json.dumps(data), headers=header)
    print(str(response))
    return response.text

if __name__ == '__main__':
    app.run()