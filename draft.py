import statistics
import sys


def set_corpus():  # erstellt den Korpus aus der mitgelieferten Datei
	init_corpus = []
	try:  # Korpus-file existiert nicht
		source = open('sortedCorpus.txt', encoding='utf-8')
		buffer = source.read().split('\n')
		for line in buffer:
			if len(line) > 0:
				temp = line.split('\t')
				split_word_type = temp[0].split('|')
				baseform = split_word_type[0]
				word_type = split_word_type[1]
				sentiment = temp[1]
				variants = temp[2].split(',')
				init_corpus.append(dict(baseform=baseform, type=word_type, sentiment=float(sentiment), variants=variants))
		return init_corpus
	except FileNotFoundError as e:
		print('Die Corpus-Datei ist nicht hinterlegt!')
		quit()


def analyze_sentiment(entry):
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


def verbalize_sentiment():
	sentiment = get_sentiment()
	if sentiment > 0.3:
		verbalized_sentiment = 'sehr positiv'
	elif sentiment > 0.1:
		verbalized_sentiment = 'eher positiv'
	elif sentiment > 0:
		verbalized_sentiment = 'leicht positiv'
	elif sentiment < -0.1:
		verbalized_sentiment = 'leicht negativ'
	elif sentiment < -0.3:
		verbalized_sentiment = 'sehr negativ'
	elif sentiment < 0:
		verbalized_sentiment = 'eher negativ'
	else:
		verbalized_sentiment = 'neutral'
	return verbalized_sentiment


def count_word(word):
	if flags[0]['value'] is True and word in TOP50:
		pass
	elif flags[1]['value'] is True and not word.isalpha():
		pass
	elif flags[4]['value'] is True and word in stopwords:
		pass
	else:
		if word in wordCounts:
			wordCounts[word] += 1
		else:
			wordCounts[word] = 1


def get_sentiment():
	global sentimentNeg, sentimentPos, posCount, negCount
	all_words = posCount + negCount
	pos = statistics.median(sentimentPos)
	neg = statistics.median(sentimentNeg)
	sentiment = float(posCount) / all_words * pos + float(negCount) / all_words * neg
	sentiment = round(sentiment, 4)
	# print(f'Es gibt {negCount} negative Woerter mit einem Score von {neg} und {posCount} positive Worter mit einem
	# Score von {pos}. Gewichtet ergibt das einen Score von {sentiment}.')
	return sentiment


def check_sentiment(single_word):
	for entry in corpus:
		# if len(word) == 0 or not word.isalpha():
		# continue
		if single_word == entry.get('baseform') or single_word in entry.get('variants'):
			# print(word)
			analyze_sentiment(entry)
		else:
			# print(word + ' wurde nicht im Korpus gefunden')
			continue


def get_output_number():
	all_words = len(wordCounts)
	if not flags[7]['value']:
		return int(all_words / 10)
	elif type(flags[7]['input']) is int:
		if flags[7]['input'] > len(wordCounts):
			too_many = flags[7]['input']
			print(
				f'Warnung: Kann nicht mehr als alle Wörter anzeigen! Zeige {all_words} statt der geforderten {too_many}')
			return len(wordCounts)
		else:
			return flags[7]['input']
	elif type(flags[7]['input']) is str:
		percentage = int(flags[7]['input'].strip('%'))
		if percentage > 100:
			print('Warnung: Kann nicht mehr als alle Wörter anzeigen!')
			return len(wordCounts)
		else:
			return int(len(wordCounts) / percentage)
	else:
		print('Falsche Eingabe bei -n Flag!')
		quit()


def print_output():
	if flags[5]['value']:
		sentiment = get_sentiment()
		output = 'Es gibt {} Woerter im Text, davon {} Adjektive, {} Adverbien, {} Verben und {} Substantive. ' \
				 'Die Stimmung des Textes ist mit {} {}.\n'
		print(output.format(wordCounter, adjectives, adverbs, verbs, nouns, sentiment, verbalize_sentiment()))
	output_words = get_output_number()
	print(f'Die haeufigsten {output_words} Woerter sind:\n')
	for i in range(0, output_words):
		most_common = max(wordCounts, key=lambda output_word: wordCounts[output_word])
		print(most_common + ' ' + str(wordCounts[most_common]))
		wordCounts.pop(most_common)


def set_stopwords():
	try:
		list_stopwords = open(flags[4]['source']).read().split()
		# print(stopwords)
		return list_stopwords
	except FileNotFoundError:
		print('Stopwortliste nicht gefunden!')
		quit()


def set_flags():
	init_flags = [{'name': 'notops', 'short': '-t', 'value': False},  # flags[0]
				  {'name': 'nodecs', 'short': '-w', 'value': False},  # flags[1]
				  {'name': 'caching', 'short': '-c', 'value': False},  # flags[2]
				  {'name': 'logging', 'short': '-l', 'value': False},  # flags[3]
				  {'name': 'stopwords', 'short': '-o', 'value': False, 'source': ''},  # flags[4]
				  {'name': 'sentiment', 'short': '-s', 'value': False},  # flags[5]
				  {'name': 'prompt', 'short': '-p', 'value': False},  # flags[6]
				  {'name': 'outputnumbers', 'short': '-n', 'value': False, 'input': 0}]  # flags[7]
	args = sys.argv
	if len(args) == 1:
		return init_flags
	cons_arg = ''
	for arg in args[1:]:
		if cons_arg != '':
			cons_arg = ''
			continue
		elif arg == '-o':
			index = args.index(arg)
			try:
				if args[index + 1][0].isalpha():
					cons_arg = args[index + 1]
					init_flag = init_flags[4]
					init_flag.update({'value': True})
					init_flag.update({'source': cons_arg})
				else:
					print('Geben Sie einen Dateinamen an!')
					quit()
			except IndexError:
				print('Keinen Dateinamen angegeben! -o Verwendung: -o DATEINAME')
				quit()
		elif arg == '-n':
			index = args.index(arg)
			try:
				cons_arg = args[index + 1]
				if cons_arg[0] != '-':
					init_flag = init_flags[7]
					if cons_arg.isdigit():
						abs_num = int(cons_arg)
						init_flag.update({'value': True})
						init_flag.update({'input': abs_num})
					else:
						if cons_arg[-1] == '%':
							if not cons_arg.strip('%').isdigit():
								print('Falsches Format für Flag -n!')
								quit()
							init_flag.update({'value': True})
							init_flag.update({'input': cons_arg})
						else:
							print('Falsches Format für Flag -n!')
							quit()
			except IndexError as e:
				print(e)
				quit()
		else:
			counter = 0
			for init_flag in init_flags:
				counter += 1
				if init_flag['short'] == arg:
					# print('Ändere Wert von ' + flag['name'])
					init_flag.update({'value': True})
					break
			if counter == len(init_flags):
				if arg != init_flags[len(init_flags) - 1]['short']:
					print(f'Das Argument {arg} gibt es nicht!')
					quit()
	return init_flags


flags = set_flags()
wordList = []
TOP50 = ['der', 'die', 'und', 'in', 'den', 'ist', 'das', 'mit', 'zu', 'von', 'im', 'sich', 'auf', 'Die', 'für', 'ein',
		 'nicht', 'dem', 'des', 'es', 'eine', 'auch', 'an', 'hat', 'am', 'als', 'Der', 'aus', 'werden', 'sie', 'bei',
		 'dass', 'Das', 'sind', 'wird', 'nach', 'um', 'er', 'einem', 'einen', 'einer', 'wie', 'noch', 'vor', 'haben',
		 'zum', 'war', 'über', 'aber', 'Sie']  # haeufigste 50 Woerter nach deu_newscrawl_public_2018

if flags[4]['value']:
	stopwords = set_stopwords()
if flags[5]['value']:
	corpus = set_corpus()
if flags[6]['value']:
	sourceFile = input('Bestimmen Sie eine Datei, die ausgewertet werden soll!\n')
	try:
		wordList = open(sourceFile, encoding='utf-8').read().split()
	except FileNotFoundError:
		print('Die Datei ist nicht vorhanden!')
		quit()
else:
	try:
		wordList = input().split()
	except BaseException:
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
	# print(word)
	wordCounter += 1
	word = word.strip('.,-;:!\"»«§€$%&/?()=\'')
	# print('analysiere ' + word)
	if len(word) != 0:
		count_word(word)
		if flags[5]['value']:
			check_sentiment(word)
print_output()