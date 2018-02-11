from .rss_scraper import RssArticleScraper
import requests
from bs4 import BeautifulSoup
import os

class EurogamerScraper(RssArticleScraper):

    feeds = [
        "http://www.eurogamer.net/?format=rss&type=article",
        "http://www.eurogamer.net/?format=rss&type=review",
        "http://www.eurogamer.net/?format=rss&type=preview",
        "http://www.eurogamer.net/?format=rss&type=news",
        "http://www.eurogamer.net/?format=rss&type=opinion"       
    ]

    origin = "eurogamer"
    agent = "gamingcorpus/rss/eurogamer.py"
    desc = "Eurogamer RSS feed scraper"

    def load(self):
        for feed in self.feeds:    

            rsp = requests.get(feed)
            soup = BeautifulSoup(rsp.text, "lxml")

            for item in soup.find_all("item"):

                title = item.find("title").text
                link = item.find("guid")
                url = link.text
                article_id = url.split("=")[-1]
                article_filepath = os.path.join(self.directory, "{}.json".format(article_id))     

                if not self.article_in_corpus(article_id):
                    print("scraping ...", url)
                    
                    rsp = requests.get(url)
                    article_soup = BeautifulSoup(rsp.text,"html.parser")
                    
                    content = article_soup.find("div", {"id":"content"})
                        
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
                        "url": url,
                        "title": title,
                        "author": author_name,
                        "author_id": author_id,
                        "publishing_date": publishing_date,
                        "text": text,
                        "text_html": text_html,
                        "infobox": infobox
                    }
                    self.articles.append(article)
        