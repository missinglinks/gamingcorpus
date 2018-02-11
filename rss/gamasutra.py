from .rss_scraper import RssArticleScraper
import requests
from bs4 import BeautifulSoup
import os

class GamasutraScraper(RssArticleScraper):

    feeds = [
        "http://feeds.feedburner.com/GamasutraNews"   
    ]

    origin = "gamasutra"
    agent = "gamingcorpus/rss/gamasutra.py"
    desc = "Gamasutra RSS feed scraper"

    def load(self):
        for feed in self.feeds:  
            rsp = requests.get(feed)
            soup = BeautifulSoup(rsp.text, "lxml")

            for item in soup.find_all("item"):
                title = item.find("title").text
                url = item.find("guid").text
                article_id = url.split("/")[-1].strip()

                if not self.article_in_corpus(article_id):
                    print ("sracping ... {}".format(url))
                    rsp = requests.get(url)
                    article_soup = BeautifulSoup(rsp.text, "html.parser")
                    content = article_soup.find("div", {"class":"item_body"})
                    text_html = str(content)
                    text = content.text

                    byline = article_soup.find("div", {"class": "comment_title"})
                    if byline:
                        publishing_date = byline.text.split("|")[0].strip()
                        author = byline.text.split("By")[-1].strip()
                    else:
                        byline = article_soup.find("span", {"class": "newsAuth"})
                        author = byline.text.replace("by","").split(" on ")[0].strip()
                        publishing_date = byline.text.split(" on ")[-1].strip()

                    article = {
                        "id": article_id,
                        "title": title,
                        "url": url,
                        "text": text,
                        "text_html": text_html,
                        "text": text,
                        "author": author,
                        "publishing_date": publishing_date
                    }

                    self.articles.append(article)
