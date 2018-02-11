from .rss_scraper import RssArticleScraper, remove_html
import requests
from bs4 import BeautifulSoup
import os
import html

class KotakuScraper(RssArticleScraper):

    feeds = [
        "http://kotaku.com/rss"
    ]

    origin = "kotaku"
    agent = "gamingcorpus/rss/kotaku.py"
    desc = "Kotaku RSS feed scraper"

    def load(self):
        for feed in self.feeds:  
            rsp = requests.get(feed)
            soup = BeautifulSoup(rsp.text, "lxml")

            for item in soup.find_all("item"):
                title = item.find("title").text
                publishing_date = item.find("pubdate").text
                url = item.find("link")
                article_id = item.find("guid").text
                url = "http://kotaku.com/{}".format(article_id)

                if not self.article_in_corpus(article_id):
                    print("scraping ... {}".format(url))
                    rsp = requests.get(url)
                    article_soup = BeautifulSoup(rsp.text, "html.parser")
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

                    article = {
                        "id": article_id,
                        "author": author_name,
                        "author_id": author_link,
                        "url": url,
                        "publishing_date": publishing_date,
                        "title": title,
                        "text": text,
                        "text_html": text_html
                    }
                    self.articles.append(article)
