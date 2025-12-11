#!/user/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
from sys import path
import os
import re
import logging
import subprocess
from func import main as template_main

# 載入 json 標準函式庫，處理回傳的資料格式
import json

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


try:
    with open("./templateLOKI/account.info", encoding="utf-8") as f:
        accountDICT = json.load(f)
        username = accountDICT['username']
        
except Exception as e:
    print(f"ERROR: {e}")

# 讀取 messages 模板
def load_message_template(file_path="gpt.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)["messages"]
    
# Webhook
app = Flask(__name__)

@app.route("/", methods=['POST'])

def linebot():
    
    body = request.get_data(as_text=True)                # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        access_token = os.environ.get("access_token")        # 輸入 token
        secret = os.environ.get("channel_secret")            # 輸入 secret
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINE 收到的訊息類型
        
        ############### message handling ###############
        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            print(msg)                                       # 印出內容
            
            filterLIST = []
            splitLIST = ["！", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
            refDICT = {}
            
            helloLIST = ["哈囉","嗨","你好","您好","hi","hello"]
            byeLIST = ["掰掰","掰","88","bye bye","bye","再見", "沒有", "拜拜"]
            if any(keyword in msg.lower() for keyword in helloLIST):
                line_bot_api.reply_message(tk,TextSendMessage("Hi!\n" + "我是 FOCUS TAIWAN 機器人\n請問您今天想問什麼呢?"))                                                        # 回傳文字訊息                
                
            elif any(keyword in msg.lower() for keyword in byeLIST):
                line_bot_api.reply_message(tk,TextSendMessage("掰掰，謝謝您的使用，期待下次為您服務!"))                                                        # 回傳文字訊息                
                
            else:
                try:
                    resultDICT = template_main(str(msg))   # Loki語意判斷                    
                    if resultDICT != {}:
                        replyLIST = []                        
                        if resultDICT['response'] != []:
                            for response in resultDICT['response']:
                                replyLIST.append(TextSendMessage(response))                                                     # 設定回覆字串                                    
                            replyLIST.append(TextSendMessage("希望有解答您的疑問~"))
                            line_bot_api.reply_message(tk,replyLIST)                                                        # 回傳文字訊息
                        else:
                            reply = "抱歉，我只是個機器人，沒辦法回答喔"                                                       # 回傳沒有答案時的預設回覆字串                            
                    else:
                            reply = "抱歉，我只是個機器人，沒辦法回答喔"                                                       # 回傳沒有答案時的預設回覆字串
                    line_bot_api.reply_message(tk,TextSendMessage(reply))                                           # 回傳訊息
                            
                except Exception as e:
                    print("[ERROR] => {}".format(str(e)))
                    print(body)                                             # 如果發生錯誤，印出收到的內容                    
                    reply = "抱歉發生一些問題，請再試一次！"                   # 回傳發生錯誤時預設回覆
                    line_bot_api.reply_message(tk,TextSendMessage(reply))   # 回傳訊息
                        
        else:
            reply = '不是文字，我可是不吃的喔!\n請再試一次~'   # 非文字訊息時回覆
            line_bot_api.reply_message(tk,TextSendMessage(reply)) # 回傳訊息
            
    except Exception as e:
        print("[ERROR] => {}".format(str(e)))
        print(body)                                                                       # 如果發生錯誤，印出收到的內容
        json_data = json.loads(body)                                                      # json 格式化訊息內容
        reply = "抱歉發生一些問題，請再試一次"                                              # 錯誤時回覆
        if json_data['events'] != []:
            line_bot_api.push_message(json_data['events'][0]['source']['userId'],TextSendMessage(reply)) # 回傳訊息
        
    return 'OK'                                                                       # 驗證 Webhook 使用，不能省略   

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)