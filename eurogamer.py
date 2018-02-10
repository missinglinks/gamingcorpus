import requests
import json
from bs4 import BeautifulSoup
from pit.store import Store
import lxml
import os
import time

FEEDS = [
    "http://www.eurogamer.net/?format=rss&type=article",
    "http://www.eurogamer.net/?format=rss&type=review",
    "http://www.eurogamer.net/?format=rss&type=preview",
    "http://www.eurogamer.net/?format=rss&type=news",
    "http://www.eurogamer.net/?format=rss&type=opinion"
]
OUT_FOLDER = "corpus/eurogamer"

if __name__ == "__main__":

    for feed in FEEDS:    

        rsp = requests.get(feed)
        soup = BeautifulSoup(rsp.text, "lxml")

        for item in soup.find_all("item"):

            title = item.find("title").text
            link = item.find("guid")
            url = link.text
            article_id = url.split("=")[-1]
            filename = "{}.json".format(article_id)
            if not os.path.exists("{}/{}".format(OUT_FOLDER, filename)):
                print("scraping ...", url)
                
                rsp = requests.get(url)
                article_soup = BeautifulSoup(rsp.text,"html.parser")
                
                content = article_soup.find("div", {"id":"content"})
                    
                article_title = content.find("h1").text.strip()
                
                byline = content.find("p", {"class":"byline"})
                author_link = byline.find("a")
                author_name = author_link.text
                author_id = author_link["href"].split("/")[-1]
                publishing_date = byline.find("span")["content"]

                text_html = ""
                text = ""
                section = content.find("article")
                for paragraph in section.find_all("p", {"class": None}):
                    text += "\n"+paragraph.text
                    text_html += " "+str(paragraph)
                infobox = []
                aside = content.find("aside")
                if aside:
                    for list_item in aside.find_all("li"):
                        infobox.append(list_item.text)


                article = {
                    "id": article_id,
                    "title": title,
                    "author": author_name,
                    "author_id": author_id,
                    "publishing_date": publishing_date,
                    "text": text,
                    "text_html": text_html,
                    "infobox": infobox
                }

                article_store = Store(article, origin="eurogamer.com", agent="gamingcorpus/eurogamer.py", desc="Eurogamer website scraper")
                article_store.save_to("{}/{}".format(OUT_FOLDER, filename))

                #with open("{}/{}".format(OUT_FOLDER, filename), "w") as f:
                #    json.dump(article, f)

                time.sleep(1)
            
                