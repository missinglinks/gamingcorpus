import requests
import lxml
from bs4 import BeautifulSoup
from pit.store import Store
import os
import json
import time

FEED = "http://kotaku.com/rss"
OUT_DIR = "corpus/kotaku"

if __name__ == "__main__":
    rsp = requests.get(FEED)
    soup = BeautifulSoup(rsp.text, "lxml")

    for item in soup.find_all("item"):
        title = item.find("title").text
        publishing_date = item.find("pubdate").text
        url = item.find("link")
        article_id = item.find("guid").text
        url = "http://kotaku.com/{}".format(article_id)
        filename = "{}.json".format(article_id)

        if not os.path.exists("{}/{}".format(OUT_DIR, filename)):
            print("scraping ... {}".format(url))
            rsp = requests.get(url)
            #print(rsp)
            article_soup = BeautifulSoup(rsp.text, "html.parser")
            #print(soup)
            content = article_soup.find("article")
            author = content.find("div", {"class": "author"})
            author_a = author.find("a")
            if author_a:
                author_name = author_a.text
                author_link = author_a["href"]
            else: 
                author_name = author.text
                author_link = ""
            
            text = content.find("div", {"class": "post-content"}).text
            text_html = str(content.find("div", {"class": "post-content"}))
            #print(author_name)
            #print(author_link) 
            #print(text)

            article = {
                "id": article_id,
                "author": author_name,
                "author_link": author_link,
                "url": url,
                "publishing_date": publishing_date,
                "text": text,
                "text_html": text_html
            }
            article_store = Store(article, origin="kotaku.com", agent="gamingcorpus/kotaku.py", desc="Kotaku article scraper")
            article_store.save_to("{}/{}".format(OUT_DIR, filename))

            time.sleep(1)
            

