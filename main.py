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

# logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 讀取帳號資訊
try:
    with open("./templateLOKI/account.info", encoding="utf-8") as f:
        accountDICT = json.load(f)
        username = accountDICT['username']
        
except Exception as e:
    logger.exception(f"Error loading account info")
    username = None
    
# Webhook
app = Flask(__name__)

@app.route("/", methods=['POST'])

def linebot():
    
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
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
        replySTR = "抱歉發生一些問題，請再試一次！"             # 預設回覆訊息

        ############### message handling ###############
        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            logger.info(f"Received message: {msg}")                                     # 印出內容            
            helloLIST = ["哈囉","嗨","你好","您好","hi","hello"]
            byeLIST = ["掰掰","掰","88","bye bye","bye","再見", "沒有", "拜拜"]
            if any(keyword in msg.lower() for keyword in helloLIST):
                replySTR = "Hi!\n" + "我是 FOCUS TAIWAN 機器人\n請問您今天想問什麼呢?"
                line_bot_api.reply_message(tk,TextSendMessage(replySTR))
                logger.info(f"Replied with message: {replySTR}")                                                        # 回傳文字訊息                
                
            elif any(keyword in msg.lower() for keyword in byeLIST):
                replySTR = "掰掰，謝謝您的使用，期待下次為您服務!"
                line_bot_api.reply_message(tk,TextSendMessage(replySTR))                                                        # 回傳文字訊息                
                logger.info(f"Replied with message: {replySTR}")

            else:
                try:
                    resultSTR = template_main(str(msg))   # Loki語意判斷                    
                    if resultSTR != "":
                            replySTR = resultSTR                                                                       # 回傳文字訊息
                    else:
                            replySTR = "抱歉，我只是個機器人，沒辦法回答喔"                                               # 回傳沒有答案時的預設回覆字串
                    line_bot_api.reply_message(tk,TextSendMessage(replySTR))                                           # 回傳訊息
                    logger.info(f"Replied with message: {replySTR}")                                                    # 印出回覆內容
                    
                except Exception as e:
                    logger.exception("Error processing message")
                    replySTR = "抱歉發生一些問題，請再試一次！"                   # 回傳發生錯誤時預設回覆
                    line_bot_api.reply_message(tk,TextSendMessage(replySTR))   # 回傳訊息
                    logger.info(f"Replied with message: {replySTR}")           # 印出回覆內容
        
        else:
            replySTR = '不是文字，我可是不吃的喔，請再試一次！'   # 非文字訊息時回覆
            line_bot_api.reply_message(tk,TextSendMessage(replySTR)) # 回傳訊息
            logger.info("Received non-text message.")

    except Exception:
        logger.exception(f"Error handling request")
        json_data = json.loads(body)                                                        # json 格式化訊息內容
        replySTR = "抱歉發生一些問題，請再試一次"                                             # 錯誤時回覆
        if json_data['events'] != []:
            line_bot_api.push_message(json_data['events'][0]['source']['userId'],TextSendMessage(replySTR)) # 回傳訊息
        
    return 'OK'                                                                       # 驗證 Webhook 使用，不能省略   

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)