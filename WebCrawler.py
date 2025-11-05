from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pypdf import PdfReader
from collections import deque
import requests
import urllib.robotparser
import time
import os
import shutil
import nltk

class WebCrawler:
    def __init__(self):
        self.startURL = ""
        self.domain = ""
        robotParser = None
        visited = None
        queue = None
    
    def getStartURL(self):
        return self.startURL
    
    def getDomain(self):
        return self.domain
    
    def getRobotParser(self):
        return self.robotParser
    
    def getVisited(self):
        return self.visited
    
    def getQueue(self):
        return self.queue

    def setStartURL(self, startURL):
        self.startURL = startURL
    
    def setDomain(self, domain):
        self.domain = domain
    
    def setRobotParser(self, robotParser):
        self.robotParser = robotParser
    
    def setVisited(self, visited):
        self.visited = visited
    
    def setQueue(self, queue):
        self.queue = queue

    def crawl(self, indexer):
        docID = 0

        while self.queue and indexer.hasReachedFullCapacity() is False:
            url = self.queue.popleft()
            if url in self.visited:
                continue
            else:
                self.visited.add(url)
                docID += 1
            
            # Check robots.txt permissions
            if not self.robotParser.can_fetch("*", url):
                print(f"Skipping (disallowed by robots.txt): {url}")
                continue
            
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                continue
            
            #Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            #Extract and save text
            text = soup.get_text(separator=" ", strip=True)
            with open("downloads/page_text.txt", "a", encoding="utf-8") as f:
                
                #Write text to output file
                f.write(f"\n\n--- PAGE {docID}: {url} ---\n{text}")

                #Feed text one token at a time to the inverted index
                text = soup.get_text(separator=" ", strip=True).strip()
                tokens = nltk.word_tokenize(text)

                position = 1
                for token in tokens:
                    if indexer.hasReachedFullCapacity() is True:
                        return
                    else:
                        indexer.add(token, docID, position)
                        position += 1
            
            #Find PDF links
            for link in soup.find_all("a", href=True):
                link_url = urljoin(url, link["href"])
                if link_url.endswith(".pdf") and self.domain in urlparse(link_url).netloc:
                    pdf_name = link_url.split("/")[-1]
                    pdf_path = os.path.join("downloads", pdf_name)
                    try:
                        pdf = requests.get(link_url)
                        with open(pdf_path, "wb") as f:
                            f.write(pdf.content)
                            print(f"Downloaded PDF: {pdf_name}")
                    except Exception as e:
                        print(f"Failed to download {link_url}: {e}")

                    #Feed text one token at a time to the inverted index
                    reader = PdfReader(pdf_path)
                    for i in range(len(reader.pages)):
                        page = reader.pages[i]
                        text = page.extract_text().strip()
                        tokens = nltk.word_tokenize(text)

                        position = 1
                        for token in tokens:
                            if indexer.hasReachedFullCapacity() is True:
                                return
                            else:
                                indexer.add(token, docID, position)
                                position += 1
                
                #Add new links to crawl
                if self.domain in urlparse(link_url).netloc and link_url not in self.visited:
                    self.queue.append(link_url)
            
            #Be polite
            time.sleep(2)
    
    def run(self, indexer):
        #Set base URL
        self.setStartURL("https://spectrum.library.concordia.ca/")
        self.setDomain("library.concordia.ca")

        #Set up robots.txt parser
        self.setRobotParser(urllib.robotparser.RobotFileParser())
        self.getRobotParser().set_url(f"https://{self.getDomain()}/robots.txt")
        self.getRobotParser().read()

        #Keep track of visited URLs
        self.setVisited(set())
        self.setQueue(deque([self.getStartURL()]))

        #Make an output folder for PDFs or text (first delete folder and its contents if they already exist)
        myDir = "downloads"
        if os.path.exists(myDir) and os.path.isdir(myDir):
            shutil.rmtree(myDir)
            print("Directory '{myDir}' and its contents deleted.")

        os.makedirs("downloads", exist_ok = True)

        self.crawl(indexer)