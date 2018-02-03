import requests
import json
from pit.store import Store
from bs4 import BeautifulSoup
import lxml
import time
import os

FEEDS = [
    "http://feeds.ign.com/ign/game-reviews",
    "http://feeds.ign.com/ign/games-articles"
]

OUT_FOLDER = "corpus/ign"

if __name__ == "__main__":
    
    for feed in FEEDS:
        rsp = requests.get(feed)

        soup = BeautifulSoup(rsp.text, "lxml")
        
        for item in soup.find_all("item"):
            title = item.find("title").text.strip()

            item_link = item.find("a")
            if item_link:
                url = item_link["href"]
                filename = "{}.json".format(url.replace("http://www.ign.com/articles/", "").replace("/","-"))
                author = item.find("dc:creator").text
                publishing_date = item.find("dc:date").text

                if not os.path.exists("{}/{}".format(OUT_FOLDER, filename)) and "articles" in url:
                    print("scraping ... {}".format(url))
                    rsp = requests.get(url, headers={"User-Agent": "gc-agent"})
                    article_soup = BeautifulSoup(rsp.text, "html.parser")
                    content = article_soup.find("div", {"class": "article-content"})
   
                    subhead = content.find("div", {"class": "article-subhead"})

                    text = subhead.text.replace("Share.", "").strip()+"\n"
                    for paragraph in content.find_all("p"):
                        if paragraph.text.strip() != "Exit Theatre Mode":
                            text += paragraph.text.strip()+"\n"

                    article = {
                        "url": url,
                        "author": author,
                        "title": title,
                        "publishing_date": publishing_date,
                        "text": text
                    }

                    article_store = Store(article, origin="ign.com", agent="gamingcorpus/ign.py", desc="IGN article scraper")
                    article_store.save_to("{}/{}".format(OUT_FOLDER, filename))

                    time.sleep(1)
            