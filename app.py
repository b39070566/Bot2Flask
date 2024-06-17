# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import random

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, StickerSendMessage, ImageSendMessage, AudioSendMessage, VideoSendMessage

import requests
from bs4 import BeautifulSoup

import phonetic as ph
from phonetic import read

import openai

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
openai_key = os.getenv('OPENAI_KEY', None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


ph_function = False
gpt_mode = False

class WordGuessingGame:
    def __init__(self):
        self.playing = False
        self.target_word = ""

    def start_game(self):
        self.playing = True
        # Replace the word list with your own set of words
        word_list = ["apple", "banana", "orange", "grape", "kiwi", "strawberry", "watermelon", "lemon", "mango", "peach", "pear", "guava", "pineapple"]
        self.target_word = random.choice(word_list)
        return TextSendMessage(text="猜單字，詞的長度為{}個字母，請輸入一個字母或整個單字 提示:水果".format(len(self.target_word)))


    def guess(self, user_input):
        if len(user_input) == 1:
            # Guessing a single letter
            if user_input in self.target_word:
                return TextSendMessage(text="正確！{}在單字中".format(user_input))
            else:
                return TextSendMessage(text="錯誤！{}不在單字中".format(user_input))
        elif len(user_input) == len(self.target_word):
            # Guessing the entire word
            if user_input == self.target_word:
                self.playing = False
                return TextSendMessage(text="猜中了！正確答案是{}".format(self.target_word))
            else:
                return TextSendMessage(text="錯誤！猜的單字不正確")
        else:
            return TextSendMessage(text="請輸入一個字母或整個單字")

word_guessing_game = WordGuessingGame()

class NumberGuessingGame:
    def __init__(self):
        self.playing = False
        self.target_number = 0
        self.counting_number = 0

    def start_game(self):
        self.counting_number = 0
        self.playing = True
        self.target_number = random.randint(1, 100)
        return TextSendMessage(text="猜數字1-100")

    def guess(self, user_input):
        user_guess = int(user_input)
        self.counting_number += 1
        if user_guess > self.target_number:
            return TextSendMessage(text="小一點")
        elif user_guess < self.target_number:
            return TextSendMessage(text="大一點")
        elif user_guess == self.target_number:
            self.playing = False
            return TextSendMessage(text="猜中了! 你總共猜了{}次".format(self.counting_number))

number_guessing_game = NumberGuessingGame()

def gpt( api_key, word ):
    openai.api_key = api_key 

    response = openai.chat.completions.create(
      model = "gpt-3.5-turbo",
      temperature = 0.9,
      max_tokens = 100,
      messages = [
        {"role": "user", "content": word }
      ]
    )

    gpt_says = (response['choices'][0]['message']['content'])
    return gpt_says

def getNews(n=10):
    url = "https://www.cna.com.tw/list/aall.aspx"
    html = requests.get(url)
    html.encoding ='utf-8'

    soup = BeautifulSoup(html.text, 'html.parser')
    # print(soup.title.string.strip())
    all = soup.find(id='jsMainList').find_all('li')

    rr = ""
    for idx,i in enumerate(all[:n]):
        mlink = i.a.get('href')
        mtext = i.find('h2').text
        mdate = i.find('div',class_='date').text
        rr += " ".join((str(idx+1), mdate, mtext, mlink, "\n"))
    return rr

def getNews2(n=3):
    url = "https://www.mnd.gov.tw/"
    html = requests.get(url)
    html.encoding ='utf-8'

    soup = BeautifulSoup(html.text, 'html.parser')
    # print(soup.title.string.strip())
    all = soup.select('#textlb01 ul li')

    rr = ""
    for idx,i in enumerate(all[:n]):
        mlink = i.find('a', class_='headline')['href']
        mtext = i.find('a', class_='headline').text
        mdate = i.find('div', class_='date').text
        rr += " ".join((str(idx + 1), mdate, mtext, mlink, "\n"))
    return rr

def getGasolinePrice():
    url = "https://www2.moeaea.gov.tw/oil111"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    price = soup.find_all("div", class_="grid_tab_content")

    pp = price[1].find_all("strong")

    rr = ""
    rr += "92 無鉛汽油 " + pp[0].text +" 元/公升\n"
    rr += "95 無鉛汽油 " + pp[1].text +" 元/公升\n"
    rr += "98 無鉛汽油 " + pp[2].text +" 元/公升\n"
    rr += "超級柴油 " + pp[3].text +" 元/公升"

    return rr

def getInvoice():
    url = "https://invoice.etax.nat.gov.tw"
    html = requests.get(url)
    html.encoding ='utf-8'
    soup = BeautifulSoup(html.text, 'html.parser')

    period = soup.find("a", class_="etw-on")
    rr = period.text+"\n"

    nums = soup.find_all("p", class_="etw-tbiggest")
    rr += "特別獎：" + nums[0].text + "\n"
    rr += "特獎：" + nums[1].text + "\n"
    rr += "頭獎：" + nums[2].text.strip() +" "+ nums[3].text.strip() +" "+ nums[4].text.strip()
    return rr

@app.route("/callback", methods=['POST'])
def callback():
    global ph_function
    global gpt_mode
    global openai_key

    if request.method == 'POST':
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return abort(400)
        except LineBotApiError:
            return abort(400)


        for event in events:
            # 若有訊息事件
            if isinstance(event, MessageEvent):
                msg = event.message.text
                # 回傳收到的文字訊息
                if msg == "猜數字":
                    returned_message = number_guessing_game.start_game()
                    line_bot_api.reply_message(event.reply_token, returned_message)
                
                elif msg == "注音":
                    if ph_function:
                        ph_function = False
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="注音模式已關閉"))
                    else:
                        ph_function = True
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="注音模式已開啟"))

                elif msg.lower() == "gpt":
                    if gpt_mode:
                        gpt_mode = False
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="AI模式已關閉"))
                    else:
                        gpt_mode = True
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="AI模式已開啟"))

                elif gpt_mode:
                    returned_message = gpt(openai_key,msg)
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=gpt_says))

                elif ph_function:
                    returned_message = ph.read(msg)
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=returned_message))

                elif number_guessing_game.playing and msg.isdigit():
                    returned_message = number_guessing_game.guess(msg)
                    line_bot_api.reply_message(event.reply_token, returned_message)

                elif msg == "猜單字":
                    returned_message = word_guessing_game.start_game()
                    line_bot_api.reply_message(event.reply_token, returned_message)

                elif word_guessing_game.playing and msg.isalpha():
                    returned_message = word_guessing_game.guess(msg.lower())
                    line_bot_api.reply_message(event.reply_token, returned_message)

                elif msg == "統一發票" or msg == "發票":
                    Invoice = getInvoice()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=Invoice))

                elif msg == "油價":
                    GasolinePrice = getGasolinePrice()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=GasolinePrice))
                        
                elif msg == "新聞":
                    News = getNews()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=News))

                elif msg == "軍事":
                    News2 = getNews2()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=News2))

                elif msg == "喵喵":
                    line_bot_api.reply_message(
                        event.reply_token,
                        StickerSendMessage(package_id=1, sticker_id=2))

                elif msg == "林襄":
                    image_urls = [
                        'https://s.yimg.com/ny/api/res/1.2/qGUq9eZftFfkgDwA6J8mcQ--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTE0NDA7Y2Y9d2VicA--/https://media.zenfs.com/ko/news_tvbs_com_tw_938/0b727f92c662723bd9941fcaac52b5bd',
                        'https://attach.setn.com/newsimages/2022/09/01/3805758-PH.jpg',
                        'https://images.chinatimes.com/newsphoto/2023-11-03/1024/20231103003058.jpg',
                        'https://s.yimg.com/ny/api/res/1.2/H_z17aILl883n2Nz5cxrTA--/YXBwaWQ9aGlnaGxhbmRlcjt3PTY0MDtoPTgwMQ--/https://media.zenfs.com/zh-tw/setn.com.tw/3ef844aae990f868d9e0fadf19ee72fe',
                        'https://obs.line-scdn.net/0hMr3CcEnQEl0OOgaykLhtCjZsHiw9XAhULAxcaSw7Hj8hFlZYYQxBPi5uSHFwXgIMLgsObCpqH20gCQULMw/w1200',
                    ]
                    selected_image_url = random.choice(image_urls)

                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(original_content_url=selected_image_url,
                        preview_image_url=selected_image_url))
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg))

        return 'OK'
    else:
        return abort(400)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
