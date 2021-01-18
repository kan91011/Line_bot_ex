
# coding: utf-8

# In[ ]:



# In[ ]:


'''

整體功能描述

應用伺服器主結構樣板
    用來定義使用者傳送消息時，應該傳到哪些方法上
        比如收到文字消息時，轉送到文字專屬處理方法

消息專屬方法定義
    當收到文字消息，從資料夾內提取消息，並進行回傳。
    
啟動應用伺服器    

'''


# In[ ]:


'''

Application 主架構

'''

# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json

# 載入基礎設定檔
secretFileContentJson=json.load(open("./line_secret_key",'r',encoding='utf8'))

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/material" , static_folder = "./material/")

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# In[ ]:


'''

消息判斷器

讀取指定的json檔案後，把json解析成不同格式的SendMessage

讀取檔案，
把內容轉換成json
將json轉換成消息
放回array中，並把array傳出。

'''

# 引用會用到的套件
from linebot.models import (
    ImagemapSendMessage,TextSendMessage,ImageSendMessage,LocationSendMessage,FlexSendMessage,VideoSendMessage
)

from linebot.models.template import (
    ButtonsTemplate,CarouselTemplate,ConfirmTemplate,ImageCarouselTemplate
    
)

from linebot.models.template import *

def detect_json_array_to_new_message_array(fileName):
    
    #開啟檔案，轉成json
    with open(fileName,'r',encoding='utf8') as f:
        jsonArray = json.load(f)
    
    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')
        
        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'audio':
            returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'video':
            returnArray.append(VideoSendMessage.new_from_json_dict(jsonObject))    


    # 回傳
    return returnArray


# In[ ]:


'''

handler處理關注消息

用戶關注時，讀取 素材 -> 關注 -> reply.json

將其轉換成可寄發的消息，傳回給Line

'''

# 引用套件
from linebot.models import (
    FollowEvent
)

# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    
    # 讀取並轉換
    result_message_array =[]
    replyJsonPath = "material/follow/reply.json"
    result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )

    # 從follow資料夾內，取出圖文選單id，並告知line，綁定用戶
    linkRichMenuId = open("material/follow/rich_menu_id", 'r').read()
    line_bot_api.link_rich_menu_to_user(event.source.user_id, linkRichMenuId)
    

# 爬蟲並將資料回傳
import requests
from bs4 import BeautifulSoup
import json

# 當文字訊息出現，根據訊息去爬蟲
# 爬CPBL

from datetime import date


def cpbl_game():
    response = requests.get(
        "https://www.msn.com/zh-tw/sports/cpbl/schedule",
        headers={
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",

        }
    )
    response.encoding = "utf-8"
    # print(response.text)
    b1 = BeautifulSoup(response.text, "html.parser")
    # print(b1.text)
    today = date.today()
    today = str(today).replace("-", "")
    game = b1.find("div", {"id": today})

    match_even = game.find("tr", {"class": "even"})

    if match_even != None:
        infor = match_even.attrs["data-m"]
        match_1 = infor.split('"')[-6]
    else:
        match_1 = ''

    match_odd = game.find("tr", {"class": "odd"})
    if match_odd != None:
        infor = match_odd.attrs["data-m"]
        match_2 = infor.split('"')[-6]
    else:
        match_2 = ''

    game_time = game.find_all("div", {"class": "hidedownlevel"})

    text = ''
    if match_1 != '':
        text += match_1 + " \n" + str(game_time[0].text.strip(" CST")) + "\n"

    if match_2 != '':
        text += match_2 + " \n" + str(game_time[1].text.strip(" CST"))

    if text == '':
        text = "今天沒有比賽喔!"
    return text

def cpbl_rank():
    response = requests.get("https://www.brothers.tw/")

    b1 = BeautifulSoup(response.text, "html.parser")
    ranks = b1.find("table", {"class":"tableType01"})
    text = "排名 隊伍   勝  和  敗     勝率   勝差\n"

    stats = ranks.find_all("tr")

    for stat in stats:
        i = 0
        trs = stat.find_all("td", {"class":"text115"})

        for tr in trs:
            if i == 1:
                text += tr.text[0:2] + "   "
            else:
                text += tr.text + "   "
            i += 1
        text += "\n"
    return text


# 爬體育新聞
def cpbl_news():
    response = requests.get(
        "https://news.google.com/search?q=%E4%B8%AD%E8%8F%AF%E8%81%B7%E6%A3%92&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant",
        params={"q": "%E4%B8%AD%E8%8F%AF%E8%81%B7%E6%A3%92",
                "hl": "zh-TW",
                "gl": "TW",
                "ceid": "TW%3Azh-Hant"}
    )
    response.encoding = "utf-8"
    b1 = BeautifulSoup(response.text, "html.parser")

    news = b1.find_all('h3', {"class": "ipQwMb"})
    num = 0
    text = ""
    for new in news:
        if num < 3:
            t = new.find("a", {"class": "DY5T1d"})
            url = "https://news.google.com" + t.get("href")[1:]
            title = t.text
            text += title + "\n"
            text += url + "\n"
            num += 1
        else:
            break
    return text


def sbl_news():
    response = requests.get(
        "https://news.google.com/search",
        params={"q": "sbl",
                "hl": "zh-TW",
                "gl": "TW",
                "ceid": "TW%3Azh-Hant"}
    )
    response.encoding = "utf-8"
    b1 = BeautifulSoup(response.text, "html.parser")
    news = b1.find_all('h3', {"class": "ipQwMb"})
    text = ""
    num = 0
    for new in news:
        if num < 3:
            t = new.find("a", {"class": "DY5T1d"})
            url = "https://news.google.com" + t.get("href")[1:]
            title = t.text
            text += title + "\n"
            text += url + "\n"
            num += 1
        else:
            break
    return text

from datetime import datetime
import time


def sbl_game():
    today = date.today()
    today = str(today).replace("-", "/")

    game1 = today + " 04:00:00"
    d = datetime.strptime(game1, "%Y/%m/%d %H:%M:%S")
    game1 = str(int(d.timestamp()) * 1000)

    game2 = today + " 08:00:00"
    d = datetime.strptime(game2, "%Y/%m/%d %H:%M:%S")
    game2 = str(int(d.timestamp()) * 1000)

    text = ""
    response = requests.get(
        "https://sleague.tw/jsons/games/1/17/gamelist.json",
        params={"nocache": "1587853070487"})
    response.encoding = "utf8"
    json_to_text = json.loads(response.text)
    loc, time, name_1, name_2 = '', '', '', ''
    for key, value in json_to_text.items():

        if key == game1 or key == game2:
            for key_2, value_2 in value[0].items():
                loc = value[0]["location"]
                time = value[0]["playTime"]
                name_1 = value[0]["teamGuest"]["name"]
                name_2 = value[0]["teamHome"]["name"]
            text += name_1 + " " + name_2 + "  " + time + "  " + loc
    if text == "":
        text = "今天沒比賽喔!"

    return text

# 'location' 'playTime' 'playDate' 'name' 'teamGuest' 'teamHome'

    
# In[ ]:


'''

handler處理文字消息

收到用戶回應的文字消息，
按文字消息內容，往素材資料夾中，找尋以該內容命名的資料夾，讀取裡面的reply.json

轉譯json後，將消息回傳給用戶

'''

# 引用套件
from linebot.models import (
    MessageEvent, TextMessage
)

# 文字消息處理
@handler.add(MessageEvent, message=TextMessage)
def process_text_message(event):
    if event.message.text == "我想看今天中職的賽程":
        a = cpbl_game()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )
    elif event.message.text == "我要看中職戰績排行":
        a = cpbl_rank()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )

    elif event.message.text == "我想看今天中職比分":
        a = "歡迎到這裡看今天比分喔!\nhttp://www.cpbl.com.tw/games/box.html?&game_type=01&game_id=20&game_date=2020-04-25&pbyear=2020"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )

    elif event.message.text == "我想看今天中職的賽事":
        a = "歡迎到下面的網站去觀看比賽喔!\n\nLINE TODAY:\nhttps://today.line.me/tw/article/本週賽程表-0PDKRp?_trms=4bab180e55d9d0c5.1587850407234\n\nYahoo:\nhttps://tw.tv.yahoo.com/cpbl/\n\n麥卡貝:\nhttps://sports.camerabay.tv/category/CPBL/1\n\nTwitch:\n\nhttps://www.twitch.tv/elevensportstw/\nhttps://www.twitch.tv/momo_sports\nhttps://www.twitch.tv/brothers_baseball\n"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )

    elif event.message.text == "我想看今天sbl比分":
        a = "歡迎到這裡看今天比分喔!\nhttps://sleague.tw/gameList.html"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )
    elif event.message.text == "我想看今天sbl的賽程":
        a = sbl_game()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )

    elif event.message.text == "我想看今天sbl的賽事":
        a = "歡迎到下面的網站去觀看比賽喔!\n\nTwitch:\nhttps://www.twitch.tv/elevensportstw2/videos"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )
    elif event.message.text == "我要看sbl戰績排行":
        a = "這裡能看到戰積排行喔!\n\nhttps://sleague.tw/index.html"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )

    elif event.message.text == "我想要看你發功預測sbl!!":
        a = "痾...這功能還沒開通喔! 敬請期待! 先看一些相關新聞吧!!!\n" + sbl_news()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )

    elif event.message.text == "我想要看你發功預測中華職棒!!":
        a = "痾...這功能還沒開通喔! 敬請期待! 先看一些相關新聞吧!!!" + cpbl_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a)
        )

    else:

        # 讀取本地檔案，並轉譯成消息
        result_message_array = []
        replyJsonPath = "material/" + event.message.text + "/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )



# In[ ]:


'''

handler處理Postback Event

載入功能選單與啟動特殊功能

解析postback的data，並按照data欄位判斷處理

現有三個欄位
menu, folder, tag

若folder欄位有值，則
    讀取其reply.json，轉譯成消息，並發送

若menu欄位有值，則
    讀取其rich_menu_id，並取得用戶id，將用戶與選單綁定
    讀取其reply.json，轉譯成消息，並發送

'''
from linebot.models import (
    PostbackEvent
)

from urllib.parse import parse_qs 

@handler.add(PostbackEvent)
def process_postback_event(event):
    
    query_string_dict = parse_qs(event.postback.data)
    
    print(query_string_dict)
    if 'folder' in query_string_dict:
    
        result_message_array =[]

        replyJsonPath = 'material/'+query_string_dict.get('folder')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif 'menu' in query_string_dict:
 
        linkRichMenuId = open("material/"+query_string_dict.get('menu')[0]+'/rich_menu_id', 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
        
        replyJsonPath = 'material/'+query_string_dict.get('menu')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )


# In[ ]:


'''

Application 運行（開發版）

'''
# if __name__ == "__main__":
#     app.run(host='0.0.0.0')


# In[ ]:


'''

Application 運行（heroku版）

'''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])

