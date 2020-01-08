#!/usr/bin/python3.8
import re, statistics, string, sys

def setCorpus (): # erstellt den Korpus aus der mitgelieferten Datei
	corpus = []
	try: #Korpus-file existiert nicht
		source = open('sortedCorpus.txt', encoding='utf-8')
		buffer = source.read().split('\n')
		for line in buffer:
			if len(line) > 0:
				temp = line.split('\t')
				splitWordType = temp[0].split('|')
				baseform = splitWordType[0]
				type = splitWordType[1]
				sentiment = temp[1]
				variants = temp[2].split(',')
				corpus.append(dict(baseform = baseform, type = type, sentiment = float(sentiment), variants=variants))
	
		return corpus
	except:
		print('Die Corpus-Datei ist nicht hinterlegt!')
		quit()

def incTextStuff (entry):
	if entry.get('type') == 'VVINF':
		global verbs
		verbs = verbs + 1
	elif entry.get('type') == 'ADJX':
		global adjectives
		adjectives = adjectives + 1
	elif entry.get('type') == 'ADV':
		global adverbs
		adverbs = adverbs + 1
	elif entry.get('type') == 'NN':
		global nouns
		nouns = nouns + 1
	if entry.get('sentiment') < 0:
		global sentimentNeg, negCount
		sentimentNeg.append(entry.get('sentiment'))
		negCount += 1
	else:
		global sentimentPos, posCount
		sentimentPos.append(entry.get('sentiment'))
		posCount += 1

def verbalizeSentiment ():
	sentiment = getSentiment()
	if sentiment > 0.3:
		verbalizedSentiment = 'sehr positiv'
	elif sentiment > 0.1:
		verbalizedSentiment = 'eher positiv'
	elif sentiment > 0:
		verbalizedSentiment = 'leicht positiv'
	elif sentiment < -0.1:
		verbalizedSentiment = 'leicht negativ'
	elif sentiment < -0.3:
		verbalizedSentiment = 'sehr negativ'
	elif sentiment < 0:
		verbalizedSentiment = 'eher negativ'
	else:
		verbalizedSentiment = 'neutral'
	return verbalizedSentiment

def countWord (word):
	if flags[0]['value'] == True and word in TOP50:
		pass
	elif flags[1]['value'] == True and not word.isalpha():
		pass
	elif flags[4]['value'] == True and word in stopwords:
		pass
	else:
		if word in wordCounts:
			wordCounts[word] += 1
		else:
			wordCounts[word] = 1

def getSentiment():
	global sentimentNeg, sentimentPos, posCount, negCount
	allWords = posCount + negCount
	pos = statistics.median(sentimentPos)
	neg = statistics.median(sentimentNeg)
	sentiment = float(posCount)/allWords * pos + float(negCount)/allWords * neg
	sentiment = round(sentiment, 4)
	#print(f'Es gibt {negCount} negative Woerter mit einem Score von {neg} und {posCount} positive Worter mit einem Score von {pos}. Gewichtet ergibt das einen Score von {sentiment}.')
	return sentiment

def checkSentiment (word):
	for entry in corpus:
		#if len(word) == 0 or not word.isalpha():
			#continue
		if word == entry.get('baseform') or word in entry.get('variants'):
			#print(word)
			incTextStuff(entry)
		else:
			#print(word + ' wurde nicht im Korpus gefunden')
			continue
def printOutput():
	if flags[5]['value'] == True:
		sentiment = getSentiment()
		output= 'Es gibt {} Woerter im Text, davon {} Adjektive, {} Adverbien, {} Verben und {} Substantive. Die Stimmung des Textes ist mit {} {}.\n'
		print(output.format(wordCounter, adjectives, adverbs, verbs, nouns, sentiment, verbalizeSentiment()))
	outputWords = int(len(wordCounts) / 10)
	print(f'Die haeufigsten {outputWords} Woerter sind:\n')
	for i in range(0, outputWords):
		mostCommon = max(wordCounts, key = lambda outputWords: wordCounts[outputWords])
		print(mostCommon + ' ' + str(wordCounts[mostCommon]))
		wordCounts.pop(mostCommon)
def setStopwords():
	try: 
		stopwords = open(flags[4]['source']).read().split()
		#print(stopwords)
		return stopwords
	except:
		print('Stopwortliste nicht gefunden!')
		quit()

def setFlags():
	flags = [{'name': 'notops', 'short': '-t', 'value': False}, #flags[0]
		 {'name': 'nodecs', 'short': '-w', 'value': False}, #flags[1]
		 {'name': 'caching', 'short': '-c', 'value': False}, #flags[2]
		 {'name': 'logging', 'short': '-l', 'value': False}, #flags[3]
		 {'name': 'stopwords', 'short': '-o', 'value': False, 'source': ''}, #flags[4]
		 {'name': 'sentiment', 'short': '-s', 'value': False}, #flags[5]
		 {'name': 'prompt', 'short': '-p', 'value': False}] #flags[6]
	args = sys.argv
	if len(args) == 1:
		return flags
	consArg = ''
	for arg in args[1:]:
		counter = 0
		if consArg != '':
			consArg = ''
			continue
		elif arg == '-o':
			index = args.index(arg)
			try:
				if args[index + 1][0].isalpha():
					consArg = args[index + 1]
					flag = flags[4]
					flag.update({'value': True})
					flag.update({'source': consArg})
				else:
					print('Geben Sie einen Dateinamen an!')
					quit()
			except:
				print('Keinen Dateinamen angegeben! -o Verwendung: -o DATEINAME')
				quit()
					
		else:
			for flag in flags:
				counter += 1
				if flag['short'] == arg:
					#print('Ändere Wert von ' + flag['name'])
					flag.update({'value': True})
					break
			if counter == len(flags):
				if arg != flags[len(flags)-1]['short']:
					print(f'Das Argument {arg} gibt es nicht!')
					quit()
	return flags

flags = setFlags()

TOP50 = ['der', 'die', 'und', 'in', 'den', 'ist', 'das', 'mit', 'zu', 'von', 'im', 'sich', 'auf', 'Die', 'für', 'ein', 'nicht', 'dem', 'des', 'es', 'eine', 'auch', 'an', 'hat', 'am', 'als', 'Der', 'aus', 'werden', 'sie', 'bei', 'dass', 'Das', 'sind', 'wird', 'nach', 'um', 'er', 'einem', 'einen', 'einer', 'wie', 'noch', 'vor', 'haben', 'zum', 'war', 'über', 'aber', 'Sie'] #haeufigste 50 Woerter nach deu_newscrawl_public_2018

if flags[4]['value'] == True:
	stopwords = setStopwords()
if flags[5]['value'] == True:
	corpus = setCorpus()
if flags[6]['value'] == True:
	sourceFile = input('Bestimmen Sie eine Datei, die ausgewertet werden soll!\n')
	try:
		wordList = open(sourceFile, encoding = 'utf-8').read().split()
	except:
		print('Die Datei ist nicht vorhanden!')
		quit()
else:
	try:
		wordList = input().split()
	except:
		print('FEHLER!')
		quit()
wordCounter = 0
adjectives = 0
adverbs = 0
verbs = 0
nouns = 0
sentimentPos = []
sentimentNeg = []
posCount = 0
negCount = 0
wordCounts = dict()
for word in wordList:
	#print(word)
	wordCounter += 1
	word = word.strip('.,-;:!\"»«§$%&/?()=\'')
	#print('analysiere ' + word)
	if len(word) != 0:
		countWord(word)
		if flags[5]['value'] == True:
			checkSentiment(word)
printOutput()

