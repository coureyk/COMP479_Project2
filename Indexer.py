from Strategies import *

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from MyCrawler.MyCrawler.spiders.WebCrawler import WebCrawler

import os
import time

class Dictionary:
    def __init__(self):
        self.vocabulary = {}

    def getVocabulary(self):
        return self.vocabulary
    
    def getSize(self):
        return len(self.vocabulary)
    
    def setVocabulary(self, vocabulary):
        self.vocabulary = vocabulary
    
    def add(self, term, postingsList):
        if term not in self.vocabulary:
            self.vocabulary[term] = postingsList
        else:
            self.vocabulary[term].add(postingsList)
    
    def sort(self):
        if self.getSize() <= 1:
            return
        
        vocabulary = self.vocabulary

        terms = list(vocabulary.keys())
        terms.sort()

        sortedVocabulary = {term: vocabulary[term] for term in terms}
        self.setVocabulary(sortedVocabulary)
        
    def searchFor(self, term):
        if term in self.vocabulary:
            return self.getVocabulary()[term]
        else:
            return None


class PostingsList:
    def __init__(self, contents = None):
        self.contents = {}
        if contents is not None:
            self.contents = contents #Stores a dictionary of the form: {docID: [positions]}

    def getContents(self):
        return self.contents
    
    def getSize(self):
        return len(self.contents)
    
    def setContents(self, contents):
        self.contents = contents
    
    def add(self, newPostingsList):
        newContents = newPostingsList.getContents()
        for docID in newContents:
            if docID in self.contents:
                self.contents[docID].extend(newContents[docID])
            else:
                self.contents[docID] = newContents[docID]

    def sort(self):
        if self.getSize() <= 1:
            return
        
        docIDs = list(self.contents.keys())
        docIDs.sort()

        sortedPL = {docID: sorted(self.contents[docID]) for docID in docIDs}
        self.setContents(sortedPL)

    def toString(self):
        if not self.contents:
            return ""
        else:
            return ", ".join(f"{docID}{positions}" for docID, positions in self.contents.items())


class InvertedIndex:
    def __init__(self):
        self.dictionary = Dictionary()
        self.strategy = None
        self.capacity = 0
        self.numOfDocumentsCollected = 0

    def getDictionary(self):
        return self.dictionary

    def getStrategy(self):
        return self.strategy
    
    def getCapacity(self):
        return self.capacity
    
    def getNumOfDocumentsCollected(self):
        return self.numOfDocumentsCollected
    
    def setDictionary(self, dictionary):
        self.dictionary = dictionary
    
    def setStrategy(self, strategy):
        self.strategy = strategy

    def setCapacity(self, capacity):
        self.capacity = capacity

    def setNumOfDocumentsCollected(self, amount):
        self.numOfDocumentsCollected = amount
    
    def add(self, token, docID, position):
        postingsList = PostingsList({docID: [position]})
        self.strategy.add(token, postingsList, self.getDictionary())

    def hasReachedFullCapacity(self):
        if self.getDictionary().getSize() == self.getCapacity():
            return True
        else:
            return False

    def chooseStrategy(self):
        validInput = False
        while not validInput:
            userInput = input("Choose a strategy (BSBI or SPIMI): ").strip().upper()
            if userInput == "BSBI":
                validInput = True
                self.setStrategy(BSBI())

                #DELETE ONCE BSBI IS IMPLEMENTED
                validInput = False
                print("Yeah... I don't think so, buddy. Choose again.\n")
            elif userInput == "SPIMI":
                validInput = True
                self.setStrategy(SPIMI())
            else:
                print("Invalid strategy entered. Please try again.\n")

    def populate(self):
        process = CrawlerProcess(get_project_settings())
        process.crawl(WebCrawler, index = self)
        process.start()

    def sort(self):
        self.strategy.sort(self)

    def writeToFile(self, filename):
        MY_FILE = os.path.join(os.getcwd(), filename)
        
        vocabulary = self.getDictionary().getVocabulary()
        with open(MY_FILE, "w", encoding = "utf-8") as f:
            for term in vocabulary:
                postingsList = vocabulary[term]
                docFrequency = postingsList.getSize()

                f.write(f"{term} ({docFrequency}) --> {postingsList.toString()}\n")

        print(f"Index contents have been stored at {MY_FILE}\n")

    def display(self):
        vocabulary = self.getDictionary().getVocabulary()
        for term in vocabulary:
            postingsList = vocabulary[term]
            docFrequency = postingsList.getSize()

            print(f"{term} ({docFrequency}) --> {postingsList.toString()}")
    
    def run(self):
        self.chooseStrategy() #Choose whether you want to populate index using BSBI or SPIMI
        self.setCapacity(None) 
        print()
        
        start = time.perf_counter()
        self.populate()
        end = time.perf_counter()
        elapsed = end - start
        print(f"\nPopulating time: {elapsed:.4f} seconds.\n")
        
        start = time.perf_counter()
        self.sort()
        end = time.perf_counter()
        elapsed = end - start
        print(f"Sorting time: {elapsed:.4f} seconds.\n")

        self.writeToFile(r"Results\myResults.txt")