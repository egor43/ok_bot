from flask import Flask
from flask import request

import base64
import urllib
import json
import requests

app = Flask(__name__)

# Group's token
token = None
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

@app.route('/settoken/<bot_token>', methods=['GET'])
def set_token(bot_token):
    bot_token = decode_parameter(bot_token)
    if not bot_token:
        return "Error! Token is none."
    global token
    token = bot_token
    return token

@app.route('/setwebhook/<webhook_address>', methods=['GET'])
def set_webhook(webhook_address):
    webhook_address = decode_parameter(webhook_address)
    if not webhook_address:
        return "Error! No webhook address."
    data = {'url': webhook_address}
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

def decode_parameter(parameter):
    if not parameter:
        return None
    parameter_b64 = urllib.parse.unquote(parameter)
    return base64.b64decode(parameter_b64).decode()

if __name__ == '__main__':
    app.run()