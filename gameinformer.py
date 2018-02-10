import requests
from urllib.parse import quote, unquote
import lxml
from bs4 import BeautifulSoup
from pit.store import Store
import os
import json
import time
import html
import re

HTML_REGEX = re.compile('<.*?>')

def remove_html(html_str):
  rv = re.sub(HTML_REGEX, '', html_str)
  return rv

FEEDS = [
    "http://www.gameinformer.com/feeds/thefeedrss.aspx",
    "http://www.gameinformer.com/b/mainfeed.aspx?Tags=preview",
    "http://www.gameinformer.com/b/mainfeed.aspx?Tags=review",
    "http://www.gameinformer.com/b/mainfeed.aspx?Tags=feature",
    "http://www.gameinformer.com/b/mainfeed.aspx?Tags=news",
    "http://www.gameinformer.com/blogs/editors/b/mainfeed.aspx?GroupID=8"
]
OUT_DIR = "corpus/gameinformer"


if __name__ == "__main__":
    for feed in FEEDS:
        rsp = requests.get(feed)

        soup = BeautifulSoup(rsp.text, "lxml")
        
        for item in soup.find_all("item"):
            #print(item)

            link = item.find("link")
            url = str(link.next_sibling)

            filename = url.split("/archive/")[-1]
            filename = filename.replace(".aspx", ".json").replace("/","-")

            if not os.path.exists("{}/{}".format(OUT_DIR, filename)):
                print ("scraping ... {}".format(url))

                title = item.find("title").text.strip()
                author = item.find("dc:creator").text.strip()
                publishing_date = item.find("pubdate").text.strip()
                text_html = html.unescape(item.find("description").text)
                text = remove_html(text_html)
                category = url.split("/archive/")[0].split("/")[-1]
                #print(category)                

                article = {
                    "title": title,
                    "url": url,
                    "author": author,
                    "category": category,
                    "publishing_date": publishing_date,
                    "text_html": text_html,
                    "text": text
                }

                article_store = Store(article, origin="gameinformer.com", agent="gamingcorpus/gameinformer.py", desc="Gameinformer article scraper")
                article_store.save_to("{}/{}".format(OUT_DIR, filename))
        