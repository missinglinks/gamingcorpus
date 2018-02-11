from .rss_scraper import RssArticleScraper, remove_html
import requests
from bs4 import BeautifulSoup
import os
import html

class GameinformerScraper(RssArticleScraper):

    feeds = [
        "http://www.gameinformer.com/feeds/thefeedrss.aspx",
        #"http://www.gameinformer.com/b/mainfeed.aspx?Tags=preview",
        #"http://www.gameinformer.com/b/mainfeed.aspx?Tags=review",
        #"http://www.gameinformer.com/b/mainfeed.aspx?Tags=feature",
        #"http://www.gameinformer.com/b/mainfeed.aspx?Tags=news",
        #"http://www.gameinformer.com/blogs/editors/b/mainfeed.aspx?GroupID=8"
    ]

    origin = "gameinformer"
    agent = "gamingcorpus/rss/gameinformer.py"
    desc = "Gameinformer RSS feed scraper"

    def load(self):
        for feed in self.feeds:  
            rsp = requests.get(feed)
            soup = BeautifulSoup(rsp.text, "lxml")
            
            for item in soup.find_all("item"):
                link = item.find("link")
                url = str(link.next_sibling)

                article_id = url.split("/archive/")[-1]
                article_id = article_id.replace(".aspx", "").replace("/","-").strip()

                if not self.article_in_corpus(article_id):
                    print ("scraping ... {}".format(url))

                    title = item.find("title").text.strip()
                    author = item.find("dc:creator").text.strip()
                    publishing_date = item.find("pubdate").text.strip()
                    text_html = html.unescape(item.find("description").text)
                    text = remove_html(text_html)
                    category = url.split("/archive/")[0].split("/")[-1]

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
