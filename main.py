from datetime import datetime
from pprint import pprint
from getnewsarticle import get_cna_article_text
from num2ap import number_to_ap
from templatePOC.main import askLoki



if __name__ == "__main__":

    inputurl = input("Please enter the CNA news URL: ")
    contentSTR = get_cna_article_text(inputurl)
    print(contentSTR)

    filterLIST = []
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    # 設定參考資料
    refDICT = { # value 必須為 list
        "open":[],
        "close":[],
        "usd_up_down":[],
        "up_down_num":[],
        "range":[],
        "turnover":[]
    }

    # 執行 Loki
    resultDICT = askLoki(contentSTR, filter=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    pprint(resultDICT)

    if resultDICT:
        weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][datetime.now().weekday()]
        if resultDICT["usd_up_down"] == "rose":
            tmpSTR = "shedding"
            hi_low = "lower"
        else:
            tmpSTR = "gaining"
            hi_low = "higher"

        turnover_num = number_to_ap(float(resultDICT["turnover"][0])) 
        # 根據 resultDICT 產生回覆內容
        templateSTR = f"U.S. dollar closes {hi_low} on Taipei forex market\n\n(Taipei,{turnover_num}) The U.S. dollar {resultDICT["usd_up_down"][0]} against the Taiwan dollar {weekday}, {tmpSTR} NT${resultDICT["up_down_num"][0]} to close at NT${resultDICT["close"][0]}.\n\nTurnover totaled US${resultDICT["turnover"][0]} billion during the trading session.\n\nThe greenback opened at NT${resultDICT["open"][0]}, and moved between NT${resultDICT["range"][0][0]} and NT${resultDICT["range"][0][1]} before the close.\n\n(By xxx)\nEnditem"

        print(templateSTR)