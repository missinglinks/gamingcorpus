from .rss_scraper import RssArticleScraper, remove_html
import requests
from bs4 import BeautifulSoup
import os
import html

class GamespotScraper(RssArticleScraper):

    feeds = [
        "https://www.gamespot.com/feeds/reviews/",
        "https://www.gamespot.com/feeds/mashup/",
        "https://www.gamespot.com/feeds/mashup/"
    ]

    origin = "gamespot"
    agent = "gamingcorpus/rss/gamespot.py"
    desc = "Gamespot RSS feed scraper"

    def load(self):
        for feed in self.feeds:  
            rsp = requests.get(feed, headers=self.headers)
            soup = BeautifulSoup(rsp.text, "lxml")
            
            for item in soup.find_all("item"):
                #print(item)
                
                link = item.find("link")
                url = str(link.nextSibling)
                #print(url)
                article_id = url.replace("https://www.gamespot.com/", "")
                article_id = article_id.replace("/","-").strip()
                category = article_id.split("-")[0]
                
                #print(article_id)
                if not self.article_in_corpus(article_id):
                    print ("scraping ... {}".format(url))

                    title = item.find("title").text.strip()

                    print(title)

                    author = item.find("dc:creator").text.strip()
                    pubdate = item.find("pubDate")
                    if not pubdate:
                        pubdate = item.find("pubdate")
                    publishing_date = pubdate.text.strip()
                    text = item.find("description").text
                    text_html = str(item.find("description"))
                    #print(text)

                    article = {
                        "id": article_id,
                        "title": title,
                        "url": url,
                        "author": author,
                        "category": category,
                        "publishing_date": publishing_date,
                        "text_html": text_html,
                        "text": text
                    }
                    self.articles.append(article)
