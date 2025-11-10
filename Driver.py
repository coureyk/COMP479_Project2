from Indexer import *
from QueryProcessor import *
from Ranker import *
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans

import numpy as np
import pandas as pd
import os

def clusterDocs(index):
    vocabulary = index.getDictionary().getVocabulary()
    terms = list(vocabulary.keys())
    docIDs = list(range(1, index.getNumOfDocumentsCollected() + 1))

    #Initialize Document-Term Matrix
    dtm = np.zeros((len(docIDs), len(terms)))

    #Fill matrix with term frequencies
    for j, term in enumerate(terms):
        for docID, positions in vocabulary[term].getContents().items():
            i = docIDs.index(docID)
            dtm[i, j] = len(positions)  #term frequency == count of positions

    #Wrap in a DataFrame for readability
    dtmDF = pd.DataFrame(dtm, index = docIDs, columns = terms)

    #Create sparse matrix that can be used for clustering
    tfidf = TfidfTransformer()
    tfidfMatrix = tfidf.fit_transform(dtmDF.values)
    
    #Cluster Using K-Means
    resultsDir = os.path.join(os.getcwd(), "Results")
    clusterInfoPath = os.path.join(resultsDir, "clusterInfo.txt")
    numOfClusters = 0
    
    with open(clusterInfoPath, 'w', encoding = "utf-8") as f:
        for i in range(3):
            match i:
                case 0:
                    numOfClusters = 2
                case 1:
                    numOfClusters = 10
                case 2:
                    numOfClusters = 20

            #Verify that numOfDocumentsCollected is >= numOfClusters (if not, exception will be thrown)
            if index.getNumOfDocumentsCollected() < numOfClusters:
                f.write(f"\n\nCannot perform k-means clustering when k > {index.getNumOfDocumentsCollected()} (i.e. the # of documents collected).")
                break

            kmeans = KMeans(n_clusters = numOfClusters, random_state=42)
            kmeans.fit(tfidfMatrix)

            labels = kmeans.labels_

            #Inspect Results
            print(f"\n\nk = {numOfClusters}\n")
            clusteredDocs = pd.DataFrame({
                "docID": docIDs,
                "cluster": labels
            })
            print(clusteredDocs)

            #See which terms are most characteristic of each cluster
            orderCentroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            terms = np.array(terms)
            
            for i in range(numOfClusters):
                f.write(f"Cluster {i}:\n")
                f.write(", ".join(terms[orderCentroids[i, :50]]))  # top 50 terms
                f.write("\n")

def main():    
    index = InvertedIndex()
    index.run()

    qp = QueryProcessor(index.getStrategy())
    qp.run(index)

    clusterDocs(index)

    
    """
    if index.hasRankingEnabled() is True and qp.getRetrievedDocs() is not None:
        Ranker.run(index, qp)
    """

if __name__ == "__main__":
    main()