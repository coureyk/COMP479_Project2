from Indexer import *
from QueryProcessor import *

def main():    
    index = InvertedIndex()
    index.run()

    qp = QueryProcessor()
    qp.run(index)

    while True:
        usrInput = input("Enter a term, docID pair: ").split()
        term = Normalization.normalize(usrInput[0])
        docID = int(usrInput[1])
        
        print(f"Term Frequency for ({usrInput[0]}, {usrInput[1]}) = {index.getDictionary().getTermFrequency(term, docID)}")
        usrInput = input("Continue? (Enter Y/N): ").strip().lower()

        if usrInput == "y" or usrInput == "yes":
            continue
        elif usrInput == "n" or usrInput == "no":
            break
        else:
            print("Invalid entry. Continuing")
        print()


if __name__ == "__main__":
    main()