#!/usr/local/bin/python

from time import strftime
from bs4 import BeautifulSoup
from subprocess import call

import requests
import re

r = requests.get('https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin/Mitte-Mitte_Prenzlauer-Berg-Prenzlauer-Berg_Kreuzberg-Kreuzberg_Wedding-Wedding_Schoeneberg-Schoeneberg/3,00-/-/EURO--1000,00/-/-/-/-/-/true')

soup = BeautifulSoup(r.text, 'html.parser')

links = soup.find_all('a', { 'class': 'result-list-entry__brand-title-container'})

ids = open('ids', 'a+')
ids.seek(0)

exposes = ids.readlines()
exposes = [expose.strip() for expose in exposes]

print "Working " + strftime("%Y-%m-%d %H:%M:%S")
text = ""
# for link in filtered:
for link in links:
	# remove span
	if link.h5.span:
		link.h5.span.extract()
	href = link.get('href')
	if not href:
		raise ValueError("Couldn't find expose link in " + link)

	expose = href[len('/expose/'):]
	if expose in exposes:
		continue
	text = re.sub('[()"]','',link.h5.get_text()) + '\n'
	# if text != "":
	message = 'display notification "' + text + '" sound name "Blow" with title "Neue Inserate"'
	print "\tAdding new entry: {}\n".format(expose)
	# print message
	call(["osascript", "-e", message])

	ids.write(expose+'\n')
# print infos		
