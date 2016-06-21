import os
import re
import pandas
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet as wn
#path of superfolder
st = StanfordNERTagger('C:\Users\ktwic_000\Downloads\stanford-ner-2015-04-20\classifiers\english.all.3class.distsim.crf.ser.gz','C:\Users\ktwic_000\Downloads\stanford-ner-2015-04-20\stanford-ner.jar', encoding = 'utf-8')
fileStem = "C:\Users\ktwic_000\Desktop\SASUniversityEdition\myfolders\edgar"
numFiles = len(os.listdir(fileStem)) + 1
labels = ['File Number','File Size', 'Date of Filing', 'Is 5.02', 'All Included Names', 'Relevant Sentences', 'Sentences With Date']
resultsFile = "C:\Users\ktwic_000\Desktop\SASUniversityEdition\myfolders\edgar\Test Files (1- 15,000)\\results.csv"
nameOfFile = ""
originalSize = 0
text = ""
itemsIncluded = []
prDate = "No Date Found"
names = []
final_names = []
is502 = False
previousPerson = False
i = -1
filingDate = 0
relevant_sents = []
companyname = ""
wordList = [wn.synset('elect.v.01'), wn.synset('elect.v.02'), wn.synset('appoint.v.01'), wn.synset('appoint.v.02'), wn.synset('retire.v.01'), wn.synset('retire.v.02'), wn.synset('vacate.v.01'), wn.synset('leave_office.v.01'), wn.synset('promote.v.02'), wn.synset('remove.v.02'),wn.synset('passing.n.02'),wn.synset('dismissal.n.04'), wn.synset('join.v.01'), wn.synset('succeed.v.02')]

sentences_with_date = []
for x in xrange(1, numFiles):
    #define variables
    nameOfFile = (fileStem + r"\\" + str(x) + ".txt")
    originalFile = open(nameOfFile, "r")
    originalSize = os.stat(nameOfFile).st_size
    text = originalFile.read()
    originalFile.close()
    text = re.sub('<DESCRIPTION>GRAPHIC.*</TEXT>','',text, re.DOTALL)
    text = re.sub('<[^<]+?>', '', text)
    text = re.sub('(&[^ ]{4};)', '', text)
    for line in text.splitlines():
        if 'FILED AS OF DATE:' in line:
            filingDate = line[17:]
        if 'Item' in line or 'ITEM' in line: 
            if re.search("(\d{1,3}\.\d{1,3})", line):
                itemsIncluded.append(re.search("(\d+?\.\d*)", line).group(0))
                if (re.search("(\d+?\.\d*)", line).group(0)) == '5.02':
                    is502=True
        if 'COMPANY CONFORMED NAME:' in line:
            companyname = line[25:]
    if originalSize < 5000000 and originalSize > 1000:  
        sentences = sent_tokenize(text)
        for sent in sentences:
            if (re.search('([A-Z]\w+ [1-9]*(1[0-9])*(2[0-9])*(3[0,1])*, \d{4})', sent))and is502:
                sentences_with_date.append(sent)
                words = pos_tag(word_tokenize(sent))
                for word in words:
                    if word[1] == "VB": 
                        sets = wn.synsets(word[0]) 
                        for s in sets: 
                            for w in wordList:
                                if w.path_similarity(s) > 0.3:
                                    relevant_sents.append(sent)
                            
                                            
        sents = st.tag_sents([word_tokenize(sent) for sent in sentences]) 
        for classedSent in sents:
            for word in classedSent:
                if'PERSON' in word[1] and not previousPerson:
                    i+=1
                    names.append(word[0])
                    previousPerson = True
                elif 'PERSON' in word[1]:
                    names[i] = names[i]+" " + word[0]
                    previousPerson = True
                else:
                    previousPerson = False
    elif originalSize > 1000: 
            chunks = (text[0+i:10000+i] for i in range(0, len(text), 10000))
            for chunk in chunks:
                    sentences = sent_tokenize(chunk)
                    for sent in sentences:
                        if (re.search('([A-Z]\w+ [1-9]*(1[0-9])*(2[0-9])*(3[0,1])*, \d{4})', sent) and is502):
                            words = pos_tag(word_tokenize(sent))
                            for word in words:
                                if word[1] == "VB": 
                                    sets = wn.synsets(word[0]) 
                                    for s in sets: 
                                        for w in wordList:
                                            if w.path_similarity(s) > 0.3:
                                                relevant_sents.append(sent)
                    sents = st.tag_sents([word_tokenize(sent) for sent in sentences]) 
                    for classedSent in sents:
                        for word in classedSent:
                            if'PERSON' in word[1] and not previousPerson:
                                i+=1
                                names.append(word[0])
                                previousPerson = True
                            elif 'PERSON' in word[1]:
                                names[i] = names[i]+" " + word[0]
                                previousPerson = True
                            else:
                                previousPerson = False
    else:
        continue
    
    for name in names:
        if " " in name and name not in final_names:
            final_names.append(name)
    print relevant_sents  
    print sentences_with_date          
    fileDataSet= pandas.Series([x,originalSize, filingDate, is502, final_names, relevant_sents, sentences_with_date],index = labels, dtype = object) 
    fileDataSet.to_csv(path= resultsFile, mode = "a", index = labels)
    itemsIncluded.clear()
    pressRelease = False
    names.clear()
    final_names.clear()
    
    is502 = False
    relevant_sents.clear() 
    previousPerson = False
    i=-1
    print "File",x,"processed."
    