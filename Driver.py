from Indexer import *
from QueryProcessor import *
from Ranker import *

def main():    
    index = InvertedIndex()
    index.run()

    qp = QueryProcessor(index.getStrategy())
    qp.run(index)

    if index.hasRankingEnabled() is True and qp.getRetrievedDocs() is not None:
        Ranker.run(index, qp)

if __name__ == "__main__":
    main()