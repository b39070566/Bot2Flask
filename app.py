# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, StickerSendMessage, ImageSendMessage

import random
import requests
from bs4 import BeautifulSoup
import fun  # Import the functions from fun.py

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
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

word_guessing_game = fun.WordGuessingGame()
number_guessing_game = fun.NumberGuessingGame()

@app.route("/callback", methods=['POST'])
def callback():
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
            if isinstance(event, MessageEvent):
                msg = event.message.text

                if msg == "猜數字":
                    returned_message = number_guessing_game.start_game()
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=returned_message))

                elif number_guessing_game.playing and msg.isdigit():
                    returned_message = number_guessing_game.guess(msg)
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=returned_message))

                elif msg == "猜單字":
                    returned_message = word_guessing_game.start_game()
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=returned_message))

                elif word_guessing_game.playing and msg.isalpha():
                    returned_message = word_guessing_game.guess(msg.lower())
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=returned_message))

                elif msg == "統一發票" or msg == "發票":
                    Invoice = fun.getInvoice()
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=Invoice))

                elif msg == "油價":
                    GasolinePrice = fun.getGasolinePrice()
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=GasolinePrice))

                elif msg == "新聞":
                    News = fun.getNews()
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=News))

                elif msg == "軍事":
                    News2 = fun.getNews2()
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=News2))

                elif msg == "喵喵":
                    line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id=1, sticker_id=2))

                elif msg == "林襄":
                    image_urls = [
                        'https://s.yimg.com/ny/api/res/1.2/qGUq9eZftFfkgDwA6J8mcQ--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTE0NDA7Y2Y9d2VicA--/https://media.zenfs.com/ko/news_tvbs_com_tw_938/0b727f92c662723bd9941fcaac52b5bd',
                        'https://attach.setn.com/newsimages/2022/09/01/3805758-PH.jpg',
                        'https://images.chinatimes.com/newsphoto/2023-11-03/1024/20231103003058.jpg',
                        'https://s.yimg.com/ny/api/res/1.2/H_z17aILl883n2Nz5cxrTA--/YXBwaWQ9aGlnaGxhbmRlcjt3PTY0MDtoPTgwMQ--/https://media.zenfs.com/zh-tw/setn.com.tw/3ef844aae990f868d9e0fadf19ee72fe',
                        'https://obs.line-scdn.net/0hMr3CcEnQEl0OOgaykLhtCjZsHiw9XAhULAxcaSw7Hj8hFlZYYQxBPi5uSHFwXgIMLgsObCpqH20gCQULMw/w1200',
                    ]
                    selected_image_url = random.choice(image_urls)
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=selected_image_url, preview_image_url=selected_image_url))

                elif "找圖" in msg:
                    search_keyword = msg.split("找圖 ")[1].strip()
                    selected_image_url = fun.imgsearch(search_keyword)
                    if selected_image_url.startswith("http"):
                        line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=selected_image_url, preview_image_url=selected_image_url))
                    else:
                        line_bot_api.reply_message(event.reply_token, TextMessage(text=selected_image_url))
                
                else:
                    line_bot_api.reply_message(event.reply_token, TextMessage(text=msg))

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
