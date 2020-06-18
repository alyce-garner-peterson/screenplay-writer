import os
import neuralcoref
import nltk

import spacy
import neuralcoref
import sys
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from Datasets import datasets

nlp = spacy.load('en')
coref = neuralcoref.NeuralCoref(nlp.vocab)
nlp.add_pipe(coref, name='neuralcoref')

import numpy as np
import torch
import plot_generator
tokenizer, model, PPLM = plot_generator.initialize(np,torch)

def phaseI_processStory(story):
	# Returns a list of list with the following as the content of list inside the list :>
	# 1. Dialogue-Replaced sentence from story
	# 2. Type of the Sentence : NARRATION, DIALOGUE, NEWLINE
	# 3. YES or NO string indicating whether NeuralCoref was applied to resolve reference
	# 4. If NeuralCoref was applied then The object It returned
	# 5. If the sentence is of type dialogue then its speaker
	# 6. If the sentence is of type dialogue then the corresponding dialogue
	dialogues = re.findall(r'\"(.+?)\"',story)
	dialogue_count = 0
	for dialogue in dialogues:
		qt_mark = "\"" if(story.find("\""+dialogue+"\"")!=-1) else '\''
		story = story.replace(qt_mark+dialogue+qt_mark,"<-DIALOGUE-#"+str(dialogue_count)+"#->")
		dialogue_count = dialogue_count + 1

	storylist = []
	for paragraph in story.split("\n"):
		for sentence in paragraph.split("."):
			if(len(sentence.strip())!=0):
				tmp_slist = list()
				tmp_slist.append(sentence)
				if(sentence.find("<-DIALOGUE-#")!=-1):
					tmp_slist.append("DIALOGUE")
				else:
					tmp_slist.append("NARRATION")
				tmp_slist.append("NO")
				tmp_slist.append(" ")
				tmp_slist.append(" ")
				tmp_slist.append(" ")
				storylist.append(tmp_slist)
		storylist.append(["\\n","NEWLINE"," "," "," "," "])

	for i in range(len(storylist)):
		if(storylist[i][1]=="DIALOGUE" and i>0):
			words = storylist[i][0].upper().split(" ")
			if("HE" in words or "SHE" in words or "HIM" in words or "HER" in words):
				j=i-1
				while(j>0):
					if(storylist[j][1]!="NEWLINE"):
						break
					j=j-1
				coreference_resolver_result = nlp(".".join([storylist[j][0],storylist[i][0]]))
				storylist[i][0] = coreference_resolver_result._.coref_resolved.split(".")[-1]
				storylist[i][2] = "YES"
				storylist[i][3] = str(coreference_resolver_result._.coref_clusters)

	k = 0
	s1 = {}
	for i in range(len(storylist)):
		if(storylist[i][1]=="DIALOGUE"):
			dialogue_holder = re.findall(r'<-DIALOGUE-#[0-9][0-9]*#->',storylist[i][0])[0]
			dialogue_containing_resolved_sentence = storylist[i][0].replace(dialogue_holder,"").strip()
			storylist[i][5] = dialogues[k]
			stop_words = set(stopwords.words("english"))
			d1 = nltk.word_tokenize(dialogue_containing_resolved_sentence.lower())
			d2 = [j for j in d1 if not j in stop_words]
			for w in nltk.pos_tag(d2):
				if(w[1]=="NN"):
					if(w[0].lower() in s1.keys()):
						s1[w[0].lower()] = s1[w[0].lower()]+1
					else:
						s1[w[0].lower()] = 1
			k = k + 1
	character_list = [k for k in s1.keys() if s1[k]>1]

	k = 0
	for i in range(len(storylist)):
		if(storylist[i][1]=="DIALOGUE"):
			storylist[i][4]="UNKNOWN"
			sentence = " ".join([ w if w not in datasets.wordList else "said" for w in storylist[i][0].split(" ")])
			for subsentence in sentence.split(","):
				if(subsentence.find("said")!=-1):
					for word in subsentence.split(" "):
						if(word.strip().lower() in character_list):
							storylist[i][4]=word.strip()
							break
					break
			k = k + 1
	return storylist

def phaseII_processStory(storylist):
	# Returns a list of list with the following as the content of list inside the list :>
	# 1. Dialogue-Replaced sentence from story or Generated PLOT
	# 2. Type of the Sentence : NARRATION, DIALOGUE, NEWLINE, PLOT
	# 3. YES or NO string indicating whether NeuralCoref was applied to resolve reference
	# 4. If NeuralCoref was applied then The object It returned
	# 5. If the sentence is of type dialogue then its speaker
	# 6. If the sentence is of type dialogue then the corresponding dialogue
	plotwords = []
	tmp = list()
	new_storylist = []
	tmp_storylist = []
	p_count = 0
	for sentences in storylist:
		tmp_storylist.append(sentences)
		if sentences[1]=="NEWLINE":
			if len(tmp_storylist)>0:
				new_storylist.append([p_count,"PLOT","","","",""])
				p_count = p_count + 1
			new_storylist += tmp_storylist
			tmp_storylist = []
			plotwords.append(tmp)
			tmp = list()
		elif sentences[1]=="NARRATIVE":
			tmp = tmp + sentences[0].split(" ")
		else:
			tmp = tmp + sentences[0].split(" ")
			tmp = tmp + sentences[5].split(" ")
	#print(new_storylist)
	for i in range(len(plotwords)):
		plotwords[i] = list(dict.fromkeys([ ("".join([tmpchar for tmpchar in word if tmpchar.isalpha()==True])).lower() for word in plotwords[i] if word.find("<-DIALOGUE-#")==-1 and len(word)>2 and word not in datasets.wordList]))
		plotwords[i].sort()
	plot_desc = []
	for i in plotwords:
		if len(i)>0:
			plot_desc.append(plot_generator.generate_plot(np,torch,tokenizer,model,PPLM,[i],20,1)[0])
		else:
			plot_desc.append('')
	new_storylist = [sentences if sentences[1]!="PLOT" else [plot_desc[sentences[0]],"PLOT","","","",""] for sentences in new_storylist]
	return new_storylist

def convert_to_html(output):
  responseString = ""
  for d in output:
    if(d[1]=="NARRATION"):
      responseString = responseString + d[0]
    elif(d[1]=="NEWLINE"):
      responseString = responseString + "<hr/>"
    elif(d[1]=="PLOT"):
      responseString = responseString + "<br/><h5>"+d[0]+"</h5>"
    else:
      responseString = responseString + "<br/><font color='red'><b>"+d[4]+"</b> : "+d[5]+"</font>"
      ad = ""
      for t in d[0].split(","):
        if(t.lower().find("said")==-1 and t.find("<-DIALOGUE-")==-1):
          ad = ad + t
      if(len(ad)>0):
        responseString = responseString + "<font color='green'>(("+ad+"))</font>"
      responseString = responseString+"</br>"
  return responseString


import os

if __name__=="__main__":
	print("Started!....")
	iFile = open("public\\story\\story01.txt")
	story = [s.replace('\n','') for s in iFile.readlines()]
	iFile.close()
	story = "\n".join(story)
	data = phaseI_processStory(story)
	data = phaseII_processStory(data)
	response = convert_to_html(data)
	print("<br><hr>")
	print(response)