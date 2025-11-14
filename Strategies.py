from abc import ABC, abstractmethod
from Normalization import Normalization

class Strategy(ABC):
    def __init__(self, type = "None"):
        self.type = type

    def getType(self):
        return self.type

    def setType(self, type):
        self.type = type

    @abstractmethod
    def add(self, token, posting, dictionary):
        pass

    @abstractmethod
    def sort(self, dictionary):
        pass

class BSBI(Strategy):
    def __init__(self):
        super().__init__("BSBI")

    def add(self, token, postingsList, dictionary):
        pass

    def sort(self, index):        
        pass

class SPIMI(Strategy):
    def __init__(self):
        super().__init__("SPIMI")

    def add(self, token, postingsList, dictionary):
        term = Normalization.normalize(token) #Note that Normalization.normalize either returns None or a list of Strings
        if term is None: #If term is None, then this means the token was filtered out during the normalization process and is therefore not to be added to the dictionary
            return
        
        term = term[0]
        vocabulary = dictionary.getVocabulary()
        if term in vocabulary: 
            vocabulary[term].add(postingsList)
        else:
            dictionary.add(term, postingsList)

    def sort(self, index):
        dictionary = index.getDictionary()
        dictionary.sort()
        
        vocabulary = dictionary.getVocabulary()
        for term in vocabulary:
            vocabulary[term].sort()