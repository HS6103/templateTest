import re
import requests
from bs4 import BeautifulSoup

def get_cna_article_text(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # 擷取完整標題
        raw_title = soup.select_one("title").get_text(strip=True)
        
        # 只取主標題 (去掉 "| ..." 部分)
        title = raw_title.split("|")[0].strip()

        # 擷取新聞段落
        paragraphs = soup.select("div.paragraph p")
        content = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]

        # 組合格式化文字
        body = "\n\n".join(content)

        # 移除括號內的文字和結尾
        full_text = re.sub(r'（.*?）[0-9]+\n\n本網站之文字、圖片及影音，非經授權，不得轉載、公開播送或公開傳輸及利用。', '', body)  # 移除括號內的文字


    except Exception as e:
        print(f"[ERROR] Failed to fetch article from {url}: {str(e)}")
        return ""
    
    return title, full_text

if __name__ == "__main__":
    # 測試網址
    url = "https://www.cna.com.tw/news/aipl/202507290201.aspx"
    article_text = get_cna_article_text(url)
    print(article_text)
