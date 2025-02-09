import numpy as np
import pandas as pd
import pickle
from Scoring import printScores
import re
import nltk
from nltk import WordNetLemmatizer

TRAINING_PATH = "/Users/shah/Box Sync/MIMC_v2/Corpus_TrainTest/"
TRAINING_TRUTH_PATH = "/Users/shah/Box Sync/MIMC_v2/Gold Standard/DocumentClasses.txt"
CORPUS_PATH = "/Users/shah/Developer/ShahNLP/TestNotes/Notes/"
TRUTH_PATH = "/Users/shah/Developer/ShahNLP/TestNotes/TestDocumentClasses.txt"

def getNotesAndClasses(corpusPath, truthPath, balanceClasses=False):
    truthData = pd.read_csv(truthPath, dtype={"notes": np.str, "classes": np.int}, delimiter='\t',
                            header=None).as_matrix()

    noteNames = truthData[:, 0].astype(str)
    noteClasses = truthData[:, 1]

    if balanceClasses:
        np.random.seed(8229)
        noteNames = np.array(noteNames)
        posIndices = np.where(noteClasses == 1)[0]
        negIndices = np.where(noteClasses == 0)[0]
        posNotes = noteNames[posIndices]
        negNotes = noteNames[negIndices]
        assert len(posNotes) + len(negNotes) == len(noteNames)

        selectedNegNotes = np.random.choice(negNotes, size=len(posNotes), replace=False)
        allNotes = np.concatenate((posNotes, selectedNegNotes), axis=0)
        labels = np.concatenate((np.ones(len(posNotes)), np.zeros(len(selectedNegNotes))), axis=0)

        noteNames = allNotes
        noteClasses = labels

    noteBodies = []

    for name in noteNames:
        with open(corpusPath + name + ".txt") as inFile:
            noteBodies.append(inFile.read())
    return np.array(noteBodies), noteClasses.astype(int)

def tokenizer(text):
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = [token for token in tokens if re.search('(^[a-zA-Z]+$)', token)]
    a = []
    for i in filtered_tokens:
        a.append(WordNetLemmatizer().lemmatize(i, 'v'))
    return a
    #return filtered_tokens

notes, labels = getNotesAndClasses(CORPUS_PATH, TRUTH_PATH, balanceClasses=False)

model = pickle.load(open("./SerializedModels/SVMFinal.pkl"))

predictions = model.predict(notes)

pickle.dump(predictions, open("./ErrorAnalysis/Predictions/SVM_DS_Test_Predictions.pkl", 'wb'))
printScores(labels, predictions)

