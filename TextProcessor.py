import os
import nltk
from bs4 import BeautifulSoup
nltk.download("punkt")

class TextProcessor:
    def process(SGM_DIR, indexer):
        #List containing all .sgm files from Reuters-21578
        sgmFiles = []
        for f in os.listdir(SGM_DIR):
            if f.endswith(".sgm"):
                sgmFiles.append(f)

        for file in sgmFiles:
            filepath = os.path.join(SGM_DIR, file)
            with open(filepath, 'r', encoding="latin-1") as f:
                data = f.read()
                soup = BeautifulSoup(data, "html.parser")

                #For each article in the file
                for reutersTag in soup.find_all("reuters"):
                    docID = int(reutersTag.get("newid")) #Get NEWID as the docID
                    position = 1

                    #Extract text (Title and Body) to tokenize
                    title = reutersTag.title.get_text() if reutersTag.title else ""
                    body = reutersTag.body.get_text() if reutersTag.body else ""
                    text = (title + " " + body).strip()

                    #If text is non-empty, then tokenize
                    if text:
                        tokens = nltk.word_tokenize(text)

                        #Create term-docID pairs and add to indexer
                        for token in tokens:
                            if indexer.hasReachedFullCapacity(): #Assignment Requirement
                                return
                            else:
                                indexer.add(token, docID, position)
                                position += 1

    def run(indexer):
        SGM_DIR = os.path.join(os.getcwd(), "Reuters21578")
        TextProcessor.process(SGM_DIR, indexer)