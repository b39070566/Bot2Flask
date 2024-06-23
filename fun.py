import random
import requests
from bs4 import BeautifulSoup

class WordGuessingGame:
    def __init__(self):
        self.playing = False
        self.target_word = ""

    def start_game(self):
        self.playing = True
        word_list = ["apple", "banana", "orange", "grape", "kiwi", "strawberry", "watermelon", "lemon", "mango", "peach", "pear", "guava", "pineapple"]
        self.target_word = random.choice(word_list)
        return "猜單字，詞的長度為{}個字母，請輸入一個字母或整個單字 提示:水果".format(len(self.target_word))

    def guess(self, user_input):
        if len(user_input) == 1:
            if user_input in self.target_word:
                return "正確！{}在單字中".format(user_input)
            else:
                return "錯誤！{}不在單字中".format(user_input)
        elif len(user_input) == len(self.target_word):
            if user_input == self.target_word:
                self.playing = False
                return "猜中了！正確答案是{}".format(self.target_word)
            else:
                return "錯誤！猜的單字不正確"
        else:
            return "請輸入一個字母或整個單字"

class NumberGuessingGame:
    def __init__(self):
        self.playing = False
        self.target_number = 0
        self.counting_number = 0

    def start_game(self):
        self.counting_number = 0
        self.playing = True
        self.target_number = random.randint(1, 100)
        return "猜數字1-100"

    def guess(self, user_input):
        user_guess = int(user_input)
        self.counting_number += 1
        if user_guess > self.target_number:
            return "小一點"
        elif user_guess < self.target_number:
            return "大一點"
        elif user_guess == self.target_number:
            self.playing = False
            return "猜中了! 你總共猜了{}次".format(self.counting_number)

def getNews(n=10):
    url = "https://www.cna.com.tw/list/aall.aspx"
    html = requests.get(url)
    html.encoding = 'utf-8'

    soup = BeautifulSoup(html.text, 'html.parser')
    all = soup.find(id='jsMainList').find_all('li')

    rr = ""
    for idx, i in enumerate(all[:n]):
        mlink = i.a.get('href')
        mtext = i.find('h2').text
        mdate = i.find('div', class_='date').text
        rr += "{} {} {} {}\n".format(idx + 1, mdate, mtext, mlink)
    return rr

def getNews2(n=3):
    url = "https://www.mnd.gov.tw/"
    html = requests.get(url)
    html.encoding = 'utf-8'

    soup = BeautifulSoup(html.text, 'html.parser')
    all = soup.select('#textlb01 ul li')

    rr = ""
    for idx, i in enumerate(all[:n]):
        mlink = i.find('a', class_='headline')['href']
        mtext = i.find('a', class_='headline').text
        mdate = i.find('div', class_='date').text
        rr += "{} {} {} {}\n".format(idx + 1, mdate, mtext, mlink)
    return rr

def getGasolinePrice():
    url = "https://www2.moeaea.gov.tw/oil111"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    price = soup.find_all("div", class_="grid_tab_content")

    pp = price[1].find_all("strong")

    rr = ""
    rr += "92 無鉛汽油 {} 元/公升\n".format(pp[0].text)
    rr += "95 無鉛汽油 {} 元/公升\n".format(pp[1].text)
    rr += "98 無鉛汽油 {} 元/公升\n".format(pp[2].text)
    rr += "超級柴油 {} 元/公升".format(pp[3].text)

    return rr

def getInvoice():
    url = "https://invoice.etax.nat.gov.tw"
    html = requests.get(url)
    html.encoding = 'utf-8'
    soup = BeautifulSoup(html.text, 'html.parser')

    period = soup.find("a", class_="etw-on")
    rr = period.text + "\n"

    nums = soup.find_all("p", class_="etw-tbiggest")
    rr += "特別獎：{}\n".format(nums[0].text)
    rr += "特獎：{}\n".format(nums[1].text)
    rr += "頭獎：{} {} {}".format(nums[2].text.strip(), nums[3].text.strip(), nums[4].text.strip())
    return rr

def imgsearch(searchFor):
    url = f"https://zh-tw.photo-ac.com/search/{searchFor}?page=1&color=all&modelCount=-2&orderBy=random&shape=all"
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    block = soup.find("div", class_="jsx-3990119274 gallery-images")

    if block:
        imgsrcs = block.find_all("img", attrs={"data-src": True})

        if imgsrcs:
            selected_img = random.choice(imgsrcs)
            img_url = selected_img.get('data-src')
            if img_url:
                return img_url
            else:
                return "未找到有效的圖片連結"
        else:
            return "未找到圖片連結"
    else:
        return "未找到指定的元素"

