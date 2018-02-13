import json
from pit.store import Store
import os
import requests
import lxml
from bs4 import BeautifulSoup
from .forum_scraper import ForumScraper
import time


THREAD_URL = "https://www.neogaf.com/threads/{id}/page-{page}"
TIMEOUT = 0.1

class NeogafScraper(ForumScraper):
    forums = {
        "neogaf_ot": "https://www.neogaf.com/forums/off-topic-discussion.22/page-{page}",
        "neogaf_gaming": "https://www.neogaf.com/forums/gaming-discussion.2/page-{page}",
        "neogaf_ot_community": "https://www.neogaf.com/forums/off-topic-community.20/page-{page}",
        "neogaf_gaming_community": "https://www.neogaf.com/forums/gaming-discussion.2/page-{page}"
    }

    origin = "neogaf"
    agent = "gamingcorpus/forums/neogaf.py"
    desc = "NeoGAF forum scraper"

    def get_thread_list(self, forum, url):
        thread_list = []
        for page in range(1, self.max_pages):
            print("\t\t page {}".format(page))
            rsp = requests.get(url.format(page=page))
            soup = BeautifulSoup(rsp.text, "html.parser")
            
            current_page = soup.find("a",{"class": "currentPage"})
            if not current_page:
                current_page = soup.find("li", {"class": "pageNav-page--current"})
        
            current_page = int(current_page.text)
            if current_page != page:
                break 
                
            thread_container = soup.find("div", {"class": "js-threadList"})
            for item in thread_container.find_all("div", {"class": "structItem--thread"}):
                item_title = item.find("div", {"class": "structItem-title"})
                title_link = item_title.find("a")
                thread_title = title_link.text.strip()
                thread_url = title_link["href"]
                thread_id = thread_url.split(".")[-1][:-1]
            
                first_post = item.find("div", {"class": "structItem-minor"})
                user_name_part = first_post.find("li")
                user_a = user_name_part.find("a")
                if user_a:
                    user = user_a.text.strip()
                    user_id = user_a["data-user-id"]
                else:
                    user = user_name_part.text.strip()
                    user_id = None
                start_date = first_post.find("li", {"class": "structItem-startDate"})
                start_date = start_date.find("time")["data-date-string"]
                
                meta = item.find("div", {"class": "structItem-cell--meta"})
                reply_count = meta.find("dd").text.replace(",", "")
                if reply_count.isdigit():
                    reply_count = int(reply_count)
                else:
                    reply_count = 0
                
                if thread_title.strip() != "":
                    thread_list.append({
                        "title": thread_title,
                        "id": thread_id,
                        "user": user,
                        "user_id": user_id,
                        "start_date": start_date,
                        "reply_count": reply_count
                    })
            time.sleep(TIMEOUT)        
        return thread_list

    def get_thread_posts(self, id_, start_post, end_post):
        start_page = int(start_post/50)
        end_page = int(end_post/50)
        
        posts = []
        
        for page in range(start_page+1, end_page+2):
            print("\t\t page {}".format(page))
            rsp = requests.get(THREAD_URL.format(id=id_, page=page))
            soup = BeautifulSoup(rsp.text, "html.parser")

            for article in soup.find_all("article", {"class":"message--post"}):
                post_id = article["data-content"]

                user_details = article.find("h4", {"class": "message-name"})
                user_link = user_details.find("a")
                if user_link:
                    user = user_link.text.strip()
                    user_id = user_link["data-user-id"]
                else:
                    user = user_details.text.strip()
                    user_id = None
                
                user_title = article.find("h5", {"class": "userTitle"}).text.strip()

                permalink = article.find("div", {"class": "message-permalink"})
                permalink = permalink.find("a")["href"]

                content = article.find("div", {"class": "message-cell--main"})
                date = content.find("time")["title"]

                text_container = content.find("div", {"class": "bbWrapper"})
                text = text_container.text.strip()
                text_html = str(text_container)

                posts.append({
                    "post_id": post_id,
                    "user": user,
                    "user_id": user_id,
                    "user_title": user_title,
                    "permalink": permalink,
                    "text_html": text_html,
                    "timestamp": date
                })
            
            time.sleep(TIMEOUT)
        return posts