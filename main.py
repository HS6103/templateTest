from datetime import datetime
from pprint import pprint
from getnewsarticle import get_cna_article_text
from tw2us import twd2usd
from conv2ap import number_to_ap, month_to_ap
from templatePOC.main import askLoki

def getTemplateTopic(titleSTR):
    filterLIST = []
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    # 設定參考資料
    refDICT = { # value 必須為 list
        "open":[],
        "close":[],
        "usd_up_down":[],
        "up_down_num":[],
        "range":[],
        "turnover":[],
        "intent":[]
    }
    # Loki 分析標題
    titleResultDICT = askLoki(titleSTR, filter=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    pprint(titleResultDICT)

    intentSTR = titleResultDICT["intent"][0]

    return intentSTR



if __name__ == "__main__":

    inputurl = input("Please enter the CNA news URL: ")
    titleSTR, contentSTR = get_cna_article_text(inputurl)
    print(contentSTR)

    topicSTR = getTemplateTopic(titleSTR)
    print(f"Identified topic: {topicSTR}")

    filterLIST = []
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    # 設定參考資料
    refDICT = { # value 必須為 list
        "open":[],
        "close":[],
        "usd_up_down":[],
        "up_down_num":[],
        "taiex_up_down_perc":[],
        "taiex_up_down":[],
        "taiex_point":[],
        "stock_point":[],
        "range":[],
        "turnover":[]
    }


    # 執行 Loki 分析內文
    resultDICT = askLoki(contentSTR, filter=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    pprint(resultDICT)

    if resultDICT:
        # 初始化當日日期變數
        today = datetime.today()
        weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][datetime.now().weekday()]
        month = month_to_ap(datetime.now().strftime('%B'))
        day = today.strftime("%d").lstrip("0")  # remove leading zero
        date = f"{month} {day}"

        # 根據不同主題填入對應的新聞稿模板
        # 台股開盤
        if topicSTR == "stock_open":
            if resultDICT["taiex_up_down"][0] == "up":
                hi_low = "higher"
            else:
                hi_low = "lower"

            turnover_num = number_to_ap(float(resultDICT["turnover"][0])) 
            usd_turnover_num = twd2usd(float(resultDICT["turnover"][0]))
            usd_turnover_AP = number_to_ap(int(usd_turnover_num))
            templateSTR = f"Taiwan shares open {hi_low}\n\n(Taipei, {date}) (CNA) The Taiwan Stock Exchange's main index opened {resultDICT["taiex_up_down"][0]} {resultDICT["up_down_num"][0]} points at {resultDICT["taiex_point"][0]} {weekday} on turnover of NT${turnover_num} (US${usd_turnover_AP}). \n\n(By xxx)\nEnditem"
        
        # 台股收盤
        elif topicSTR == "stock_close":
            hi_low = resultDICT["taiex_up_down"][0] # "up" or "down"
            turnover_num = number_to_ap(float(resultDICT["turnover"][0])) 
            usd_turnover_num = twd2usd(float(resultDICT["turnover"][0]))
            usd_turnover_AP = number_to_ap(int(usd_turnover_num))
            templateSTR = f"Taiwan shares close {hi_low} {resultDICT["taiex_up_down_perc"][0]} \n\n(Taipei, {date}) (CNA) Taiwan shares ended {hi_low} {resultDICT["up_down_num"][0]} points, or {resultDICT["taiex_up_down_perc"][0].replace("%"," percent")}, at {resultDICT["stock_point"][0]} {weekday} on turnover of NT${turnover_num} (US${usd_turnover_AP}). \n\n(By xxx)\nEnditem"
        
        # 台幣收盤
        elif topicSTR == "ntd_close":

            if resultDICT["usd_up_down"][0] == "rose":
                tmpSTR = "shedding"
                hi_low = "lower"
            else:
                tmpSTR = "gaining"
                hi_low = "higher"

            turnover_num = number_to_ap(float(resultDICT["turnover"][0])) 
            # 根據 resultDICT 產生回覆內容
            templateSTR = f"U.S. dollar closes {hi_low} on Taipei forex market\n\n(Taipei, {date}) The U.S. dollar {resultDICT["usd_up_down"][0]} against the Taiwan dollar {weekday}, {tmpSTR} NT${resultDICT["up_down_num"][0]} to close at NT${resultDICT["close"][0]}.\n\nTurnover totaled US${turnover_num} during the trading session.\n\nThe greenback opened at NT${resultDICT["open"][0]}, and moved between NT${resultDICT["range"][0][0]} and NT${resultDICT["range"][0][1]} before the close.\n\n(By xxx)\nEnditem"

        print(templateSTR)