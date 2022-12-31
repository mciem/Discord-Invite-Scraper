import httpx, random, time, pystyle, json, threading, ctypes, os
from bs4 import BeautifulSoup 
from math import ceil

width = os.get_terminal_size().columns

class Console:
    def error(txt: str) -> None:
        print(" " * (((width//2))//3) + pystyle.Colors.red + "[" + pystyle.Colors.white + "!" + pystyle.Colors.red + "] " + pystyle.Colors.white + txt)

    def debug(txt: str) -> None:
        print(" " * (((width//2))//3) + pystyle.Colors.blue + "[" + pystyle.Colors.white + "^" + pystyle.Colors.blue + "] " + pystyle.Colors.white + txt)

    def good(txt: str) -> None:
        print(" " * (((width//2))//3) + pystyle.Colors.green + "[" + pystyle.Colors.white + "$" + pystyle.Colors.green + "] " + pystyle.Colors.white + "Good invite: " + pystyle.Colorate.Horizontal(pystyle.Colors.green_to_white, txt))
    
    def bad(txt: str) -> None:
        print(" " * (((width//2))//3) + pystyle.Colors.blue + "[" + pystyle.Colors.white + "*" + pystyle.Colors.blue + "] " + pystyle.Colors.white + "Bad invite: " + pystyle.Colorate.Horizontal(pystyle.Colors.blue_to_white, txt))

    def input(txt: str) -> str:
        print(" " * (((width//2))//3) + pystyle.Colors.yellow + "[" + pystyle.Colors.white + ">" + pystyle.Colors.yellow + "] " + pystyle.Colors.white + txt, end="")
        return input("")

class Scraper:
    def __init__(self):
        self.proxies = open("input/proxies.txt", "r").read().splitlines()

        self.scraped, self.good, self.invalid = 0, 0, 0
        self.start()
    
    def title(self):
        while True:
            ctypes.windll.kernel32.SetConsoleTitleW(f"Invite Scraper | mciem#0546 | Good: {str(self.good)} | Invalid: {str(self.invalid)}")
    
    def check(self, url, proxy):
        invite = url.strip("https://discord.gg/")

        headers = {
            "authority":          "discord.com",
			"accept":             "*/*",
			"accept-language":    "en-US;q=0.8,en;q=0.7",
			"content-type":       "application/json",
            "pragma":             "no-cache",
			"sec-ch-ua":          '"Chromium";v="108", "Google Chrome";v="108", "Not;A=Brand";v="99"',
			"sec-ch-ua-mobile":   "?0",
			"sec-ch-ua-platform": '"Windows"',
			"sec-fetch-dest":     "empty",
			"sec-fetch-mode":     "cors",
			"sec-fetch-site":     "same-origin",
			"user-agent":         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",}

        data = {
            "with_expiration": True,
            "inputValue": invite,
            "with_counts": True
        }

        req = httpx.get(f"https://discord.com/api/v9/invites/{invite}", headers=headers, params=data, proxies={"http://": "http://"+ proxy, "https://": "http://"+ proxy,})
        if req.status_code == 404:
            return "invalid"
        
        js = json.loads(req.text)
        return "good"

    
    def scrape(self, tag, page, proxy):
        headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US;q=0.8,en;q=0.7",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Gpc": "1",
            #"Cookie": "",
            "Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",}

        client = httpx.Client(headers=headers, proxies={"http://": "http://"+random.choice(self.proxies),"https://": "http://"+random.choice(self.proxies)}, timeout=10)

        url = "https://disboard.org/servers/tag/" + tag + "/" + str(page)

        html = client.get(url)
        soup = BeautifulSoup(html.text, "html.parser")

        Console.debug("Scraping: " + tag + " | Page: " + str(page))
        l = soup.find_all("a", {"class": "button button-join is-discord"})
        
        for link in l:
            lin = "https://disboard.org" + str(link["href"])
            code = lin.strip("https://disboard.org/server/join/")
            r = client.get("https://disboard.org/server/join/" + code)
            soup = BeautifulSoup(r, "html.parser")
            
            if r.status_code == 429:
                Console.error("You are being rate limited, changing proxy...")
                client = httpx.Client(headers=headers, proxies={"http://": "http://"+random.choice(self.proxies),"https://": "http://"+random.choice(self.proxies)}, timeout=10)
                break

            client.headers["Origin"] = "https://disboard.org"
            client.headers["X-Csrf-Token"] = soup.find("meta", {"name": "csrf-token"})["content"]
            client.headers["X-Requested-With"] = "XMLHttpRequest"
            client.headers["Content-Length"] = "0"
            client.headers["Referer"] = "https://disboard.org/server/join/" + code
            
            r1 = client.post("https://disboard.org/site/get-invite/" + code)

            invite = r1.text.replace('"', "")
            
            if 'discord.gg' in invite:
                
                Console.debug("Scraped: " + invite + ", checking...")
                self.scraped += 1
                
                c = self.check(invite, proxy)
                if c == "good":
                    Console.good(invite)
                    self.good += 1
                    f = open('output/invites.txt', "a+")
                    f.write(invite + "\n")
                    f.close()
                else:
                    Console.bad(invite)
                    self.invalid += 1

    def work(self, tag, frm, to):
        for i in range(frm, to):
            proxy = random.choice(self.proxies)
            try:
                self.scrape(tag, i, proxy)
            except Exception as e:
                Console.error(str(e))

            time.sleep(1)

    def main(self):
        threading.Thread(target=self.title).start()

        self.work_to_do = len(self.tags) * 50 # pages to scrape
        x = 50//self.threads # pages to scrape for every thread

        threads = []
        works = []

        for tag in self.tags:
            for a in range(x, 50+x, x):
                if a > 50:
                   works.append([tag, a-x, 50])
                else:
                    works.append([tag, a-x, a])
        
        random.shuffle(works)

        a = 0
        l = len(works)

        while a < l:
            if threading.active_count() < self.threads:
                x = threading.Thread(target=self.work, args=(works[a][0], works[a][1], works[a][2]))
                a+=1
                x.start()
            
            for thread in threads:
                if thread.is_alive() == False:
                    thread.join()
                    threads.remove(thread)

    def start(self):
        self.threads = int(Console.input("Threads: "))

        config = json.loads(open("input/config.json", "r").read())

        self.tags = config["tags"]

        self.main()

Scraper()        
