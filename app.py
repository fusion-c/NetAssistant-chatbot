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
from bs4 import BeautifulSoup as bs
import requests
import re

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

def checkIPflow(ip : str):
    payload = {
        "ip": ip,
        "submit": "Submit"
    }

    res = requests.post("https://uncia.cc.ncu.edu.tw/dormnet/index.php?section=netflow&sub=24hr", data=payload)
    res.encoding = "big5"
    soup = bs(res.text, "lxml")

    taglist1 = soup.find_all('tr', attrs={'bgcolor': "#ffffbb"})
    l1 = []
    for trtag in taglist1:
        s1 = trtag.text
        l1 += re.findall("\(.+\)", s1)

    taglist2 = soup.find_all('tr', attrs={'bgcolor': "#bbbbff"})
    l2 = []
    for trtag in taglist2:
        s2 = trtag.text.strip().split("\n")
        l2 = s2

    l3 = zip(l2[1:], l1)
    content = "24hr 總量"
    for a,b in l3:
        content += '{}:\t\t{}\n'.format(a, b)
    return  content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("Handle: reply_token: " + event.reply_token + ", message: " + event.message.text)
    if re.match("((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))",
                event.message.text) :
        ip = event.message.text
        content = checkIPflow(ip)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])
