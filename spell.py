#!/usr/bin/env python

import collections, os

def clean(word):
	import re
	return re.match('[^a-zA-Z]*([a-zA-Z\'-]*)[^a-zA-Z]*', word).group(1).lower()

#-----arguments-----#
import argparse
desc = '''\
a command-line spell checker for domain-specific configuration and usage

case-insensitive

By default, common English words are accepted.
"ignore groups" may be specified as options.
The following ones are provided:
- e (modern English)
- t (technical)
- html
- css
By default, e ignore group is enabled. Use
- none: to disable all ignore groups
- all: to enable all ignore groups
'''
parser=argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('file', help='file to spell check')
parser.add_argument('ignore_group', nargs='*', help='an ignore group to use', default=['e'])
args=parser.parse_args()

if args.ignore_group == ['none']:
	args.ignore_group = []
if args.ignore_group == ['all']:
	args.ignore_group = [i[:-4] for i in os.listdir('ignore')]

#-----setup-----#
home=os.path.split(os.path.realpath(__file__))[0]

if not os.path.exists(os.path.join(home, 'word_list.txt')):
	import glob
	frequency=collections.defaultdict(int)
	for path in glob.glob(os.path.join(home, 'books', '*.txt')):
		with open(path) as book:
			for word in book.read().split():
				word=clean(word)
				if not word: continue
				frequency[word]+=1
	words=[]
	for word in frequency:
		if frequency[word]>1:
			words.append(word)
	with open(os.path.join(home, 'word_list.txt'), 'w') as word_list:
		for word in words:
			word_list.write(word+'\n')

words=None
with open(os.path.join(home, 'word_list.txt')) as word_list:
	words=set(word_list.read().split())

ignores=set()
for ignore_group in args.ignore_group:
	with open(os.path.join(home, 'ignore', ignore_group+'.txt')) as ignore_list:
		ignores.update(ignore_list.read().split())

#-----processing-----#
try: input=raw_input
except NameError: pass

new_ignores=collections.defaultdict(list)

with open(args.file) as file:
	line_number=1
	quit=False
	for line in file.readlines():
		for dirty_word in line.split():
			word=clean(dirty_word)
			if not word: continue
			if word not in ignores and word not in words:
				while True:
					print('Found "{0}" on line {1}. Enter ? for help.'.format(word, line_number))
					i=input()
					if i=='?' or i=='':
						print('Enter , to continue reading through the file.')
						print('Enter . to quit, updating ignore groups.')
						print('Enter .. to quit, updating nothing.')
						print('Enter ?? to print out some context.')
						print('Enter ??? to debug.')
						print('Other inputs are interpreted as an ignore group to append the word to.')
						continue
					if i==',': break
					if i=='.': quit=True; break
					if i=='..': exit(0)
					if i=='??': print(line.strip()); print(dirty_word); continue
					if i=='???': import pdb; pdb.set_trace(); continue
					new_ignores[i].append(word)
					ignores.add(word)
					break
			if quit: break
		if quit: break
		line_number+=1

for ignore_group in new_ignores:
	with open(os.path.join(home, 'ignore', ignore_group+'.txt'), 'a') as ignore_list:
		for word in new_ignores[ignore_group]:
			ignore_list.write(word+'\n')
