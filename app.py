from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from bs4 import BeautifulSoup

app = Flask(__name__)

line_bot_api = LineBotApi('wPUDj4OWkbz3VwQTqeinJGfwm+URSwIfdtoe/TuAsHTke5sNRRbCpPzKJoK6G07DAdfJto07B4zuI54jZx1Kw8nMCJCeiaivVM4a7RtgugbsvUj91qr872eliZUQtNh0+JFcMjuzpTAy/TtR6r5tpgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('938c4bc71e35bdb85ace788a6e513d18')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("Handle: reply_token: " + event.reply_token + ", message: " + event.message.text)
    content = "{}: {}".format(event.source.user_id, event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=content))

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
