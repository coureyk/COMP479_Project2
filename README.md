# My Inverted Index Program

## Description
The purpose of this project is to implement a web crawler that will search for Master’s and PhD theses, as well as other .pdf documents within the spectrum.library.concordia.ca domain. The text from these documents is then extracted, normalized, and stored within an inverted index. A query processor is also implemented and provides users with the ability to enter conjunctive (AND) queries, which will return a list of the downloaded documents that satisfy each query. Lastly, the scikit-learn module is utilized for the purpose of clustering all downloaded documents. All code was written using Python 3.14.0.

## Installation
1. Clone the repository: https://github.com/coureyk/COMP479_Project2
2. Navigate to the project folder.
3. Install dependencies w/ the command: pip install requirements.txt

## How to Run the Program?
1. Open terminal.
2. Navigate to the project folder.
3. Enter the command: python Driver.py