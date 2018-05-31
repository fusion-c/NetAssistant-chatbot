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
    content = "24hr 總量\n"
    for a,b in l3:
        content += '{}:\t\t{}\n'.format(a, b)
    return  content

def checkTop24():
    res = requests.post("https://uncia.cc.ncu.edu.tw/dormnet/index.php?section=netflow&sub=top24")
    res.encoding = "big5"
    soup = bs(res.text, "lxml")

    tab = soup.find('table', attrs={"border": "1", "cellspacing": "0", "cellpadding": "5"})
    content = "最近 24 小時流量 (對校外上傳)十大 (單位: GB)\n"
    content += "IP Add\t\t\t上傳(校外)\t下載(校外)\t上傳 (全部)\t下載(全部)\n全宿網\t\t\t"

    count = 0
    for tr in tab.findAll('tr'):
        if count < 2:
            count += 1
            continue
        elif count == 13:
            break
        for td in tr.findAll('td'):
            content += td.getText().strip() + "\t\t"
        content += "\n"
        count += 1

    return content

def checkTop10():
    res = requests.post("https://uncia.cc.ncu.edu.tw/dormnet/index.php?section=netflow&sub=top10")
    res.encoding = "big5"
    soup = bs(res.text, "lxml")

    tab = soup.find('table', attrs={"border": "1", "cellspacing": "0", "cellpadding": "5"})
    th = soup.find("th", attrs={"colspan": "5"})

    content = th.text
    content += "\nIP Add\t\t\t上傳(校外)\t下載(校外)\t上傳 (全部)\t下載(全部)\n全宿網\t\t\t"

    count = 0
    for tr in tab.findAll('tr'):
        if count < 2:
            count += 1
            continue
        elif count == 13:
            break
        for td in tr.findAll('td'):
            content += td.getText().strip() + "\t\t"
        content += "\n"
        count += 1

    return content

def checkLimit():
    res = requests.post("https://uncia.cc.ncu.edu.tw/dormnet/index.php?section=netflow&sub=limit")
    res.encoding = "big5"
    soup = bs(res.text, "lxml")

    tab = soup.find('table', attrs={"border": "1", "cellspacing": "0", "cellpadding": "5"})
    tr = soup.find("tr", attrs={"bgcolor": "ffffbb"})

    content = tr.text
    content += "\nIP Address\t\t\t出校外上傳量\t佔總量比\t\t資料時間\t\n"

    count = 0
    for tr in tab.findAll('tr'):
        if count < 2:
            count += 1
            continue
        display = False
        for td in tr.findAll('td'):
            if display == True:
                content += td.getText().strip() + "\t\t"
            display = True
        content += "\n"
        count += 1

    return content

def checkRatio():
    res = requests.post("https://uncia.cc.ncu.edu.tw/dormnet/index.php?section=netflow&sub=ratio")
    res.encoding = "big5"
    soup = bs(res.text, "lxml")

    tab = soup.find('table', attrs={"border": "1", "cellspacing": "0", "cellpadding": "5"})
    tr = soup.find("tr", attrs={"bgcolor": "ffffbb"})

    content = tr.text
    content += "\nIP Address\t\t\t出校外上傳量\t\t出校外下載量\t\t比值\t\n"

    count = 0
    for tr in tab.findAll('tr'):
        if count < 2:
            count += 1
            continue
        if count == 13:
            break
        display = False
        for td in tr.findAll('td'):
            if display == True:
                content += td.getText().strip() + "\t\t"
            display = True
        content += "\n"
        count += 1

    return content


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("Handle: reply_token: " + event.reply_token + ", message: " + event.message.text)
    if re.match("((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))", event.message.text):
        ip = event.message.text.strip()
        content = checkIPflow(ip)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if re.sub('\s', '', event.message.text) == "24hr排行":
        content = checkTop24()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if re.sub('\s', '', event.message.text) == "10min排行":
        content = checkTop10()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if re.sub('\s', '', event.message.text) == "超量列表":
        content = checkLimit()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if re.sub('\s', '', event.message.text) == "上傳下載比":
        content = checkLimit()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

import os
if __name__ == "__main__":
    app.run()
    # app.run(host='0.0.0.0', port=os.environ['PORT'])
