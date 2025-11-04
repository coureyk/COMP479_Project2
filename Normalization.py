from abc import ABC, abstractmethod
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
nltk.download("stopwords")
nltk.download('punkt_tab')

numRemovalPattern = r"^[0-9.,](([,]*[0-9]+)+|([\.]*[0-9]+)*|([0-9]+))+[0-9.,]*$"
casefoldingPattern = r"[A-Z]"
englishStopwords = stopwords.words("english")

class NormaliztionTechnique(ABC):    
    def __init__(self):
        self.name = self.__class__.__name__

    def getName(self):
        return self.name
    
    def getNumOfTechniques():
        return len(__class__.__subclasses__())
    
    @abstractmethod
    def normalize(self, myString):
        pass

class Unfiltered(NormaliztionTechnique):
    def __init__(self):
        super().__init__()

    def normalize(self, myString):
        return myString
    
class RemoveNumbers(NormaliztionTechnique):
    def __init__(self):
        super().__init__()

    def normalize(self, myString):
        if re.search(numRemovalPattern, myString):
            return None
        else:
            return myString
        
class Casefolding(NormaliztionTechnique):
    def __init__(self):
        super().__init__()

    def normalize(self, myString):
        return myString.lower()
    
class ThirtyStopWords(NormaliztionTechnique):
    def __init__(self):
        super().__init__()

    def normalize(self, myString):
        myStopwords = set(englishStopwords[0:30])
        
        if myString in myStopwords:
            return None
        else:
            return myString

class OneHundredFiftyStopWords(NormaliztionTechnique):
    def __init__(self):
        super().__init__()
    
    def normalize(self, myString):
        myStopwords = set(englishStopwords[30:])
        
        if myString in myStopwords:
            return None
        else:
            return myString

class PorterStemming(NormaliztionTechnique):
    def __init__(self):
        super().__init__()
    
    def normalize(self, myString):
        ps = PorterStemmer()
        return ps.stem(myString)

class Normalization():
    def normalize(tokens):
        
        #If a single token is passed, convert to list that contains single token.
        if not isinstance(tokens, list):
            tokens = [tokens]

        technique = None
        normalizedTokens = []

        for i in range(len(tokens)):
            currentToken = tokens[i]
            for j in range(NormaliztionTechnique.getNumOfTechniques()):
                match j:
                    case 0:
                        technique = Unfiltered()
                    case 1:
                        technique = RemoveNumbers()
                    case 2:
                        technique = Casefolding()
                    case 3:
                        technique = ThirtyStopWords()
                    case 4:
                        technique = OneHundredFiftyStopWords()
                    case 5:
                        technique = PorterStemming()
                
                currentToken = technique.normalize(currentToken)
                if currentToken is None:
                    break

            if currentToken is not None:
                normalizedTokens.append(currentToken)
        
        if len(normalizedTokens) == 0:
            return None
        elif len(normalizedTokens) == 1:
            return normalizedTokens[0]
        else:
            return normalizedTokens