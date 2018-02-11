from .rss_scraper import RssArticleScraper, remove_html
import requests
from bs4 import BeautifulSoup
import os
import html

class IgnScraper(RssArticleScraper):

    feeds = [
        "http://feeds.ign.com/ign/game-reviews",
        "http://feeds.ign.com/ign/games-articles"
    ]

    origin = "ign"
    agent = "gamingcorpus/rss/ign.py"
    desc = "IGN RSS feed scraper"

    def load(self):
        for feed in self.feeds:  
            rsp = requests.get(feed)
            soup = BeautifulSoup(rsp.text, "lxml")
            
            for item in soup.find_all("item"):
                title = item.find("title").text.strip()

                item_links = item.find_all("a")

                if item_links:
                    item_link = item_links[-1]
                    url = item_link["href"]
                    article_id = url.split("/articles/")[-1]
                    article_id = article_id.replace("/", "-")
                    author = item.find("dc:creator").text
                    publishing_date = item.find("dc:date").text

                    if not self.article_in_corpus(article_id) and "articles" in url:
                        print("scraping ... {}".format(url))
                        rsp = requests.get(url, headers={"User-Agent": "gc-agent"})
                        article_soup = BeautifulSoup(rsp.text, "html.parser")
                        content = article_soup.find("div", {"class": "article-content"})
    
                        subhead = content.find("div", {"class": "article-subhead"})

                        text_html = str(subhead)
                        text = subhead.text.replace("Share.", "").strip()+"\n"
                        for paragraph in content.find_all("p"):
                            if paragraph.text.strip() != "Exit Theatre Mode":
                                text += paragraph.text.strip()+"\n"
                                text_html += " "+str(paragraph)

                        article = {
                            "id": article_id,
                            "url": url,
                            "author": author,
                            "title": title,
                            "publishing_date": publishing_date,
                            "text": text,
                            "text_html": text_html
                        }
                        self.articles.append(article)
