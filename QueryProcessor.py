from Normalization import *
from Indexer import *

class Query:
    def __init__(self, query):
        self.originalQuery = query
        self.normalizedQuery = Normalization.normalize(nltk.word_tokenize(query))
        self.index = InvertedIndex() #Required for determining tf-idf of query terms

    def getOriginalQuery(self):
        return self.originalQuery

    def getNormalizedQuery(self):
        return self.normalizedQuery
    
    def getIndex(self):
        return self.index
        
    def setOriginalQuery(self, originalQuery):
        self.originalQuery = originalQuery

    def setNormalizedQuery(self, normalizedQuery):
        self.normalizedQuery = normalizedQuery

    def setIndex(self, index):
        self.dictionary = index

        
class QueryProcessor:
    def __init__(self, strategy):
        self.type = "None"
        self.query = None
        self.retrievedDocs = None
        self.strategy = strategy

    def getType(self):
        return self.type

    def getQuery(self):
        return self.query
    
    def getRetrievedDocs(self):
        return self.retrievedDocs
    
    def getStrategy(self):
        return self.strategy

    def setType(self, type):
        self.type = type
    
    def setQuery(self, query):
        self.query = query

    def setRetrievedDocs(self, retrievedDocs):
        self.retrievedDocs = retrievedDocs

    def setStrategy(self, strategy):
        self.strategy = strategy

    def promptUserForQuery(self):
        validInput = False
        while not validInput:
            queryStr = input("Enter query: ").strip()
            query = Query(queryStr)

            if query.getNormalizedQuery() is not None:
                validInput = True

                query.getIndex().setStrategy(self.strategy)
                docID = 0
                position = 0
                for term in query.getNormalizedQuery():
                    query.getIndex().add(term, docID, position)
                    position += 1

                self.setQuery(query)
            else:
                print("Your search query is invalid. Please try again.\n")
    
    def intersect(query, dictionary):
        normalizedQuery = query.getNormalizedQuery()
        
        if normalizedQuery is None:
            return None
        elif isinstance(normalizedQuery, str):
            normalizedQuery = [normalizedQuery]

        targetPLs = []
        
        for termStr in normalizedQuery:
            postingsList = dictionary.searchFor(termStr)
            if postingsList is None: #If a query term does not occur in vocab., then its postings list is empty, therefore, there will be no intersection.
                return None
            else:
                targetPLs.append(postingsList)

        targetPLs.sort(key = lambda pl: pl.getSize()) #Sorts target posting lists by length in ascending order.

        intersection = list(targetPLs[0].getContents().keys())
        for currentPL in targetPLs[1:]:
            i = 0
            j = 0

            oldIDs = intersection
            curIDs = list(currentPL.getContents().keys())
            newIntersection = []
            
            while (i != len(oldIDs) and j != len(curIDs)):
                if oldIDs[i] == curIDs[j]:
                    newIntersection.append(oldIDs[i])
                    i += 1
                    j += 1
                elif oldIDs[i] < curIDs[j]:
                    i += 1
                else:
                    j += 1
            
            intersection = newIntersection

        return intersection
    
    def displayResults(self):
        retrievedDocs = self.getRetrievedDocs()

        if retrievedDocs is None or len(retrievedDocs) == 0: #If retrievedDocs is None, this is because a query term is not present within the dictionary. If len(retrievedDocs) == 0, then all query terms exist within the dictionary, but none have matching docIDs
            print("No documents returned.")
        else:
            retrievedDocsStr = ", ".join(str(docID) for docID in self.getRetrievedDocs())
            print(f"Retrieved Document IDs ({len(retrievedDocs)}): {retrievedDocsStr}")

    
    def run(self, index):
        stopRunning = False
        allRetrievedDocs = set()
        
        while stopRunning is False:
            self.promptUserForQuery()

            intersectOfTargetPLs = QueryProcessor.intersect(self.getQuery(), index.getDictionary())
            
            self.setRetrievedDocs(intersectOfTargetPLs)
            if self.getRetrievedDocs() is not None and len(self.getRetrievedDocs()) > 0:
                allRetrievedDocs.update(self.getRetrievedDocs())

            self.displayResults()
            print()
            
            while True:
                userInput = input("Would you like to enter another query? (Enter Y/N): ").strip().lower()

                if userInput == "y" or userInput == "yes":
                    break
                elif userInput == "n" or userInput == "no":
                    stopRunning = True
                    break
                else:
                    print("Invalid entry.\n")
            print()

        MY_COLLECTION = os.path.join(os.getcwd(), "Results", "My-collection.txt")
        with open(MY_COLLECTION, "w", encoding = "utf-8") as f:
            sortedDocs = sorted(allRetrievedDocs)

            if len(sortedDocs) == 0:
                f.write("No documents were retrieved during your session.")
            else:
                f.write(f"Documents retrieved ({len(sortedDocs)}): {", ".join(f"{docID}" for docID in allRetrievedDocs)}")