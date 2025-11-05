import math

class Ranker:    
    def getTermFrequency(vocabulary, term, docID):
            if term in vocabulary and docID in vocabulary[term].getContents():
                return len(vocabulary[term].getContents()[docID])
            else:
                return 0
            
    def getDocumentFrequency(vocabulary, term):
        if term in vocabulary:
            return vocabulary[term].getSize()
        else:
            return 0
        
    def getTF_IDF(vocabulary, term, docID):
        base = 10

        #Calculate TF
        rawTF = Ranker.getTermFrequency(vocabulary, term, docID)
        tf = math.log(rawTF + 1, base)

        #Calculate IDF
        rawIDF = 1 / Ranker.getDocumentFrequency(vocabulary, term) #1 should be replaced with N (where N represent the total # of documents in the corpus)
        idf = math.log(rawIDF)

        return tf * idf
    
    def getNormalizedWeight(weights):
        sumOfWeights = 0
        for weight in weights:
            sumOfWeights += weight ** 2

        return math.sqrt(sumOfWeights)
    
    def run(index, qp):
        queryTuples = [] #List of (term, weight) tuples

        queryVocab = qp.getQuery().getIndex().getDictionary().getVocabulary()
        docVocab = index.getDictionary().getVocabulary()

        similarityTuples = [] #List of (docID, cosineSimilarity) tuples

        for term in queryVocab:

            #Get weight vector for query
            tf = Ranker.getTermFrequency(queryVocab, term, docID = 0)
            idf = 1 / Ranker.getDocumentFrequency(docVocab, term) #IDF must be retrieved from original InvertedIndex (since the index within QueryProcessor will always contain exactly one docID). YOU NEED TO FIX THIS: 1 MUST BE REPLACED BY N (THE NUMBER OF DOCUMENTS IN THE CORPUS)
            weight = tf * idf
            termTuple = (term, weight)
            queryTuples.append(termTuple)

        for docID in qp.getRetrievedDocs():
            
            docTuples = [] #List of (term, weight) tuples

            #Get weight vector for document
            for term in queryVocab:
                weight = Ranker.getTF_IDF(docVocab, term, docID)
                docTuple = (term, weight)
                docTuples.append(docTuple)

            #Get cosine similarity between query and current document
            numerator = 0
            for i in range(len(queryTuples)):
                numerator += queryTuples[i][1] * docTuples[i][1]

            queryWeights = [queryTuple[1] for queryTuple in queryTuples]
            docWeights = [docTuple[1] for docTuple in docTuples]
            queryWeightsNormalized = Ranker.getNormalizedWeight(queryWeights)
            docWeightsNormalized = Ranker.getNormalizedWeight(docWeights)

            denominator = queryWeightsNormalized * docWeightsNormalized

            cosineSimilarity = numerator / denominator

            #Append similarityTuple to the similarityTuples list
            similarityTuple = (docID, cosineSimilarity)
            similarityTuples.append(similarityTuple)

        similarityTuples.sort(key=lambda myTuple: myTuple[1])
        print("Original Retrieval: ", end = "")
        qp.displayResults()
        print("Ranked retrieval: " + str(similarityTuples))