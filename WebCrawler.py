from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pypdf import PdfReader
from collections import deque
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import requests
import urllib.robotparser
import time
import os
import shutil
import nltk

class WebCrawler(CrawlSpider):
    name = "thesis"
    start_urls = ["https://spectrum.library.concordia.ca/"]
    allowed_domains = ["library.concordia.ca"]
    pdfLimit = 10
    pdfCount = 0

    rules = (
        Rule(LinkExtractor(allow="view, thesis, .html, eprint")),
        Rule(LinkExtractor(allow=".pdf"), callback="parseItem")
    )

    def parseItem(self, response):
        # Only handle PDF responses
        if response.url.endswith(".pdf"):
            myDir = "downloads"
            if os.path.exists(myDir) and os.path.isdir(myDir):
                shutil.rmtree(myDir)
                print(f"Directory '{myDir}' and its contents deleted.")
            os.makedirs(myDir)

            filename = response.url.split("/")[-1]  # e.g. thesis123.pdf
            filepath = os.path.join(myDir, filename)

            # Save the PDF file
            with open(filepath, "wb") as f:
                f.write(response.body)

            self.logger.info(f"Saved file: {filepath}")

            self.pdfCount += 1

        if self.pdfCount == self.pdfLimit:
            self.logger.info(f"PDF limit ({self.pdfLimit}) reached. Stopping crawl.")
            self.crawler.engine.close_spider(self, reason="pdf limit reached")
            return

        