from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pypdf import PdfReader
from collections import deque
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request

import requests
import os
import shutil

pdfPattern = r"\.pdf"
htmlPattern = r"^(\d{4})\.(html)$"
eprintPattern = r"id\/eprint"

class WebCrawler(CrawlSpider):
    name = "thesis"
    start_urls = ["https://spectrum.library.concordia.ca"]
    allowed_domains = ["library.concordia.ca"]
    pdfLimit = 10
    pdfCount = 0

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": True,  # Spectrum has a robots.txt; respect it.
    }

    rules = (
        Rule(LinkExtractor(allow=(pdfPattern,), deny_extensions=[], restrict_css='a.ep_document_link'), callback="parseItem"),
        Rule(LinkExtractor(allow=(htmlPattern,))),
        Rule(LinkExtractor(allow=(eprintPattern,))),
        Rule(LinkExtractor(allow=(r"thesis",))),
        Rule(LinkExtractor(allow=(r"document_subtype",)))
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.myDir = "downloads"
        if os.path.exists(self.myDir) and os.path.isdir(self.myDir):
            shutil.rmtree(self.myDir)
            print(f"Directory '{self.myDir}' and its contents deleted.")
        os.makedirs(self.myDir)

        self.downloadedFiles = []
    
    def parseItem(self, response):
        if self.pdfCount >= self.pdfLimit:
            self.logger.info(f"PDF limit ({self.pdfLimit}) reached. Stopping crawl.")
            self.crawler.engine.close_spider(self, reason="pdf_limit_reached")
            return
        
        filename = response.url.split("/")[-1]  # e.g. thesis123.pdf
        if filename in self.downloadedFiles:
            return
        
        filepath = os.path.join(self.myDir, filename)

        # Save the PDF file
        with open(filepath, "wb") as f:
            f.write(response.body)

        self.logger.info(f"Saved file: {filepath}")

        self.pdfCount += 1