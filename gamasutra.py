import requests
import lxml
from bs4 import BeautifulSoup
from pit.store import Store
import os
import json
import time

FEED = "http://feeds.feedburner.com/GamasutraNews"
OUT_DIR = "corpus/gamasutra"

if __name__ == "__main__":
    rsp = requests.get(FEED)
    soup = BeautifulSoup(rsp.text, "lxml")

    for item in soup.find_all("item"):
        #print(item)
        title = item.find("title").text
        #print(title)
        #publishing_date = item.find("pubdate").text
        url = item.find("guid").text
        #print(url)
        #article_id = item.find("guid").text
        #url = "http://kotaku.com/{}".format(article_id)
        filename = "{}.json".format(url.split("/")[-1].strip())

        if not os.path.exists("{}/{}".format(OUT_DIR, filename)):
            print ("sracping ... {}".format(url))
            rsp = requests.get(url)
            article_soup = BeautifulSoup(rsp.text, "html.parser")
            #print(article_soup)
            content = article_soup.find("div", {"class":"item_body"})
            text_html = str(content)
            text = content.text

            #print(text)

            byline = article_soup.find("div", {"class": "comment_title"})
            if byline:
                publishing_date = byline.text.split("|")[0].strip()
                author = byline.text.split("By")[-1].strip()
            else:
                byline = article_soup.find("span", {"class": "newsAuth"})
                author = byline.text.replace("by","").split(" on ")[0].strip()
                publishing_date = byline.text.split(" on ")[-1].strip()
            
            #print(publishing_date)
            #print(author)
                
            article = {
                "title": title,
                "url": url,
                "text": text,
                "text_html": text_html,
                "text": text,
                "author": author,
                "publishing_date": publishing_date
            }

            article_store = Store(article, origin="gamasutra.com", agent="gamingcorpus/gamasutra.py", desc="Kotaku article scraper")
            article_store.save_to("{}/{}".format(OUT_DIR, filename))

            time.sleep(1)
            