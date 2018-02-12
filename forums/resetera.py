import json
from pit.store import Store
import os
import requests
import lxml
from bs4 import BeautifulSoup
from .forum_scraper import ForumScraper
import time

TIMEOUT = 0.1
THREAD_URL = "https://www.resetera.com/threads/{id}/page-{page}"

class ReseteraScraper(ForumScraper):
    forums = {
        "resetera_etc": "https://www.resetera.com/forums/etcetera.9/page-{page}",
        "resetera_vg": "https://www.resetera.com/forums/video-games.7/page-{page}",
        "resetera_etc_hangouts": "https://www.resetera.com/forums/hangouts.10/page-{page}",
        "resetera_vg_hangouts": "https://www.resetera.com/forums/hangouts.8/page-{page}"
    }
    thread_list = []

    origin = "resetera"
    agent = "gamingcorpus/forums/resetera.py"
    desc = "ResetEra forum scraper"

    def get_thread_list(self, forum, url):
        for page in range(1, self.max_pages):
            print("page ",page)
            
            rsp = requests.get(url.format(page=page))
            soup = BeautifulSoup(rsp.text, "html.parser")
            
            current_page = soup.find("a",{"class": "currentPage"})
            
            current_page = int(current_page.text)
            if current_page != page:
                break 
                
            for li in soup.find_all("li", {"class": "discussionListItem"}):
                #skip sticky threads
                if "sticky" not in li["class"]:
                    title = li.find("h3")
                    thread_url = title.find("a")["href"]
                    id_ = thread_url.split(".")[-1][:-1]
                    title = title.text.strip()
                    
                    reply_count = li.find("dl", {"class": "major"}).text.replace("Posts:", "").replace(",","").strip()
                    if reply_count.isdigit():
                        reply_count = int(reply_count)
                    else:
                        reply_count = 0
                    abbr = li.find("abbr", {"class": "DateTime"})
                    
                    if not abbr:
                        date = li.find("a", {"class" : "faint"}).text
                    else:
                        date = abbr["data-datestring"]

                    user_a = li.find("a", {"class": "username"})
                    user = user_a.text.strip()
                    user_id = user_a["href"].split(".")[-1][:-1]

                    self.thread_list.append({
                        "title": title,
                        "id": id_,
                        "user": user,
                        "user_id": user_id,
                        "start_date": date,
                        "reply_count": reply_count     
                    })

            time.sleep(TIMEOUT)        

    def get_thread_posts(self, id_, start_post, end_post):
        start_page = int(start_post/50)
        end_page = int(end_post/50)
        
        posts = []
        
        for page in range(start_page+1, end_page+2):
            print("\t\t page {}".format(page))
            rsp = requests.get(THREAD_URL.format(id=id_, page=page))
            soup = BeautifulSoup(rsp.text, "html.parser")

            for message in soup.find_all("li", {"class":"message"}):
                post_id = message["id"]

                user_details = message.find("h3", {"class": "userText"})
                user_link = user_details.find("a", {"class": "username"})
                if user_link:
                    user = user_link.text.strip()
                    try:
                        user_id = user_link["href"].split(".")[-1][:-1]
                    except:
                        print(user)
                        print(user_link)
                        user_id = None
                
                user_title = []
                for user_title_element in user_details.find("em"):
                    try:
                        user_title.append(user_title_element.text.strip())
                    except:
                        #print(user_title_element)
                        user_details.append(str(user_title_element))

                abbr = message.find("abbr", {"class": "DateTime"})
                if abbr:
                    if "title" in abbr:
                        date = abbr["title"]
                    else:
                        date = abbr.text.strip()
                else:
                    date = message.find("span", {"class":"DateTime"}).text.strip()

                content = message.find("article")
                text_container = content.find("blockquote")
                text = text_container.text.strip()
                text_html = str(text_container)

                posts.append({
                    "post_id": post_id,
                    "user": user,
                    "user_id": user_id,
                    "user_title": user_title,
                    "permalink": "#{}".format(post_id),
                    "text_html": text_html,
                    "timestamp": date
                })
            
            time.sleep(TIMEOUT)
        return posts