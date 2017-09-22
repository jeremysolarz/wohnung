#!/usr/bin/env python

from time import strftime
from bs4 import BeautifulSoup
from subprocess import call

import requests
import re
import click
import configparser

config = configparser.ConfigParser()

config.read('config.ini')

def mailgun(subject, text):
	url = config['mailgun']['url']
	key = config['mailgun']['key']

	data={
		"from": "Mailgun Sandbox <postmaster@sandbox32314ac4c4224e1083144e89b3b33708.mailgun.org>",
		"to": "Jeremy Solarz <jeremy.solarz@gmail.com>",
		"subject": subject,
		"text": text
	}
	return requests.post(
		url, auth=("api", key), data=data
	)

def mac_notification(message):
	call(["osascript", "-e", message])


def pushover(message, url):
	payload = {
		"token": config['pushover']['token'],
		"user": config['pushover']['user'],
		"message": message,
		"url": url
	}
	requests.post("https://api.pushover.net/1/messages.json", data=payload)


@click.command()
@click.option('--crawl_url', help='Immoscout24 url to crawl.')
@click.option('--push', is_flag=True)
@click.option('--mac', is_flag=True)
@click.option('--mail', is_flag=True)
def client(crawl_url, push, mac, mail):
	r = requests.get(crawl_url)

	soup = BeautifulSoup(r.text, 'html.parser')

	links = soup.find_all('a', { 'class': 'result-list-entry__brand-title-container'})

	ids = open('.immoscout24_ids', 'a+')
	ids.seek(0)

	exposes = ids.readlines()
	exposes = [expose.strip() for expose in exposes]

	print "Working " + strftime("%Y-%m-%d %H:%M:%S")

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
		title = "Wohnung {}".format(expose)

		message = u'display notification "{}" sound name "Blow" with title "{}"'.format(text, title).encode('utf-8')

		url = "https://www.immobilienscout24.de/expose/{}\n".format(expose)

		print "\tAdding new entry: {}\n".format(url)

        if push:
		    pushover(message, url)
        if mac:
		    mac_notification(message)
        if mail:
            mailgun(title, url)

        ids.write(expose+'\n')

if __name__ == '__main__':
	client()