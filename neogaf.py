import requests
import json
from bs4 import BeautifulSoup
import time
import os

OUT_DIR = "corpus/neogaf"

FORUMS = {
    "neogaf_ot": "https://www.neogaf.com/forums/off-topic-discussion.22/page-{page}"
}

MAX_PAGES = 9000


THREAD = "https://www.neogaf.com/threads/{id}/page-{page}"

def get_thread_posts(id_,start_post, end_post):
    start_page = int(start_post/50)
    end_page = int(end_post/50)
    
    posts = []
    
    for page in range(start_page+1, end_page+2):
        print("\t\t page {}".format(page))
        rsp = requests.get(THREAD.format(id=id_, page=page))
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

            #print(user_id, user)

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
                "text_html": text_html
            })
        
        time.sleep(0.2)
        
        #print(date)
    return posts

def get_thread_list(forum, url):
    thread_list = []

    for page in range(1, MAX_PAGES):
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
            reply_count = int(meta.find("dd").text.replace(",", ""))
            
            thread_list.append({
                "title": thread_title,
                "id": thread_id,
                "user": user,
                "user_id": user_id,
                "start_date": start_date,
                "reply_count": reply_count
            })
        time.sleep(0.2)
        
    return thread_list




def main():

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    for forum, url in FORUMS.items():
        
        forum_dir = os.path.join(OUT_DIR, forum)
        if not os.path.exists(forum_dir):
            os.makedirs(forum_dir)

        #get recent thread list
        print("... getting new thread list")
        thread_list = get_thread_list(forum, url)

        #save new thread list
        thread_list_filepath = os.path.join(OUT_DIR, "{}.json".format(forum))
        with open(thread_list_filepath, "w") as f:
            json.dump(thread_list, f)


        #get new threads
        for thread in thread_list:

            print("\t scrape thread '{}'".format(thread["title"]))

            year = thread["start_date"].split(" ")[-1].strip()
            tmp_dir = os.path.join(forum_dir, year)
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            thread_filepath = os.path.join(tmp_dir, "{}.json".format(thread["id"]))
            if not os.path.exists(thread_filepath):
                posts = get_thread_posts(thread["id"], 0, thread["reply_count"]+1)
                thread["posts"] = posts
                
                print("\t {} posts scraped".format(len(posts)))
                print("")

                with open(thread_filepath, "w") as f:
                    json.dump(thread, f)
            time.sleep(0.2)



if __name__ == "__main__":
    main()