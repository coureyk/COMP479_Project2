from Indexer import *
from QueryProcessor import *
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
    CLUSTER_INFO_PATH = os.path.join(os.getcwd(), "Results", "clusterInfo.txt")
    numOfClusters = 0
    
    with open(CLUSTER_INFO_PATH, 'w', encoding = "utf-8") as f:
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
                f.write(f"Error: Cannot perform k-means clustering when k > total documents collected. (k = {numOfClusters}; Total Documents Collected = {index.getNumOfDocumentsCollected()})\n")
                break

            kmeans = KMeans(n_clusters = numOfClusters, random_state=42)
            kmeans.fit(tfidfMatrix)

            labels = kmeans.labels_
            
            #Write results
            f.write(f"k = {numOfClusters}\n")
            for clusterNum in range(numOfClusters):

                #Get docIDs for the current cluster and ensure they are strings
                clusterDocIDs = [str(docIDs[j]) for j in range(len(docIDs)) if labels[j] == clusterNum]

                #Join the docIDs with commas
                if clusterDocIDs:
                    f.write(f"Cluster {clusterNum}: {', '.join(clusterDocIDs)}\n")
                else:
                    f.write(f"Cluster {clusterNum}: No documents\n")
            f.write("\n")

            #See which terms are most characteristic of each cluster
            orderCentroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            terms = np.array(terms)
            
            """
            f.write("The top 50 vocabulary terms for each cluster ranked by tf/idf:\n\n")
            for i in range(numOfClusters):
                f.write(f"Cluster {i}:\n")
                f.write(", ".join(terms[orderCentroids[i, :50]]))  #Write the top 50 terms to the file
                f.write("\n\n")
            f.write("\n")
            """

            for i in range(numOfClusters):
                f.write(f"Cluster {i}:\n")

                #Get the cluster centroids (each centroid is a vector representing the average TF-IDF weight per term)
                centroid = kmeans.cluster_centers_[i]

                #Create a pandas Series from the centroid (mapping terms to their TF-IDF weights)
                centroidSeries = pd.Series(centroid, index=terms)

                # Sort top 50 terms by their TF-IDF weight (descending order)
                topTerms = centroidSeries.sort_values(ascending=False).head(50)

                # Write the top 50 terms and their TF-IDF weights to the file
                for idx, (term, weight) in enumerate(topTerms.items()):
                    if idx == len(topTerms) - 1:
                        f.write(f"{term}: {weight:.4f}")
                    else:
                        f.write(f"{term}: {weight:.4f}, ")
                f.write("\n\n")

    print(f"Clustering Results saved: {CLUSTER_INFO_PATH}")

def main():    
    index = InvertedIndex()
    index.run()

    qp = QueryProcessor(index.getStrategy())
    qp.run(index)

    clusterDocs(index)

    print("Thank you for using my Inverted Index program!\n")

if __name__ == "__main__":
    main()