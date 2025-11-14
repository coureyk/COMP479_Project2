from pypdf import PdfReader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import os
import shutil
import nltk

class WebCrawler(CrawlSpider):
    name = "thesis"
    start_urls = ["https://spectrum.library.concordia.ca"]
    allowed_domains = ["library.concordia.ca"]
    
    pdfLimit = 25

    pdfPattern = r"\.pdf"
    htmlPattern = r"(\/2\d2\d)\.(html)$" #matches with 2x1x.html (i.e. 2010+.html)
    eprintPattern = r"id\/eprint"
    thesisPattern = r"\/thesis[^\/]*\/$"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "ROBOTSTXT_OBEY": True,  # Spectrum has a robots.txt; respect it.
    }

    rules = (
        Rule(LinkExtractor(allow=(pdfPattern,), deny_extensions=[]), callback="downloadPDF"),
        Rule(LinkExtractor(allow=(htmlPattern,))),
        Rule(LinkExtractor(allow=(eprintPattern,))),
        Rule(LinkExtractor(allow=(thesisPattern,))),
        Rule(LinkExtractor(allow=(r"\/document_subtype/$",)))
    )
    
    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.index = index
        
        self.downloadsDir = os.path.join(os.getcwd(), "Downloads")
        if os.path.exists(self.downloadsDir) and os.path.isdir(self.downloadsDir):
            shutil.rmtree(self.downloadsDir)
            print(f"Directory '{self.downloadsDir}' and its contents deleted.")
        os.makedirs(self.downloadsDir)

        self.downloadedFiles = set()
    
    def downloadPDF(self, response):
        print()
        print()
        print()
        curDocID = self.index.getNumOfDocumentsCollected() + 1
        print(f"Limit: {self.pdfLimit}")
        print(f"cur docID: {curDocID}")

        filename = response.url.split("/")[-1]  # e.g. thesis123.pdf
        filename = "_".join([str(curDocID), filename])
        if curDocID > self.pdfLimit:
            self.logger.info(f"PDF limit ({self.pdfLimit}) reached. Stopping crawl.")
            self.crawler.engine.close_spider(self, reason="pdf_limit_reached")
            return
        elif self.index.hasReachedFullCapacity():
            self.logger.info(f"Index capacity ({self.index.getCapacity()}) reached. Stopping crawl.")
            self.crawler.engine.close_spider(self, reason="index_limit_reached")
            return
        elif filename in self.downloadedFiles:
            self.logger.info(f"PDF file ({self.pdfLimit}) already reached.")
            return
                
        # Save the PDF file
        pdfPath = os.path.join(self.downloadsDir, filename)
        with open(pdfPath, "wb") as f:
            f.write(response.body)

        #Feed text one token at a time to the inverted index
        hasTokens = False
        reader = PdfReader(pdfPath)
        logInfoPath = os.path.join(self.downloadsDir, f"logInfo{curDocID}.txt")
        with open(logInfoPath, 'w', encoding = "utf-8") as file:
            position = 1
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                text = page.extract_text()
                if not text:
                    self.logger.warning(f"No extractable text on page {i} of '{filename}'. Skipping page.")
                    continue
                
                text = text.strip()
                if not text:
                    self.logger.warning(f"No extractable text on page {i} of '{filename}'. Skipping page.")
                    continue

                tokens = nltk.word_tokenize(text)
                if not tokens:
                    self.logger.warning(f"No extractable tokens on page {i} of '{filename}'. Skipping page.")
                    continue

                hasTokens = True
                for token in tokens:
                    file.write(f"{token}. Doc ID: {curDocID}. Pos: {position}\n")
                    if self.index.hasReachedFullCapacity():
                        break
                    else:
                        self.index.add(token, curDocID, position)
                        position += 1

                if self.index.hasReachedFullCapacity():
                        break
        
        os.remove(pdfPath)
        if hasTokens is False:
            self.logger.warning(f"No text extracted from any page of '{filename}'. Skipping PDF.")
        else:
            self.downloadedFiles.add(filename)
            self.index.setNumOfDocumentsCollected(curDocID)

            pdfLinkPath = os.path.join(self.downloadsDir, "Links.txt")
            with open(pdfLinkPath, "a") as f:
                f.write(f"{curDocID}) {response.url}\n")

            print(f"File successfully indexed and saved within: {pdfLinkPath}")
            curDocID += 1
