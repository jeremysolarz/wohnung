#!/usr/bin/env python

from time import strftime
from bs4 import BeautifulSoup
from subprocess import call

import requests
import re
import click
import ConfigParser

config = ConfigParser.RawConfigParser()

config.read('config.ini')

def mailgun(title, text, url):
	mailgunurl = config.get('mailgun', 'url')
	key = config.get('mailgun', 'key')

	data={
		"from": "Wohnung Service <postmaster@sandbox32314ac4c4224e1083144e89b3b33708.mailgun.org>",
		"to": ["jeremy.solarz@gmail.com", "jsolarz@google.com"], # "kerstin.jarco@web.de"],
		"subject": title,
		"text": url
	}
	return requests.post(
		mailgunurl, auth=("api", key), data=data
	)

def mac_notification(title, text):
	message = u'display notification "{}" sound name "Blow" with title "{}"'.format(text, title).encode('utf-8')
	call(["osascript", "-e", message])


def pushover(title, text, url):
	message = u'{} open {}'.format(text, url).encode('utf-8')
	payload = {
		"token": config.get('pushover', 'token'),
		"user": config.get('pushover', 'user'),
		"title": title,
		"message": message,
		"url": url
	}
	requests.post("https://api.pushover.net/1/messages.json", data=payload)


@click.command()
@click.option('--crawl_url', help='Immoscout24 url to crawl.')
@click.option('--type', default="Wohnung")
@click.option('--push', is_flag=True)
@click.option('--mac', is_flag=True)
@click.option('--mail', is_flag=True)
def client(crawl_url, type, push, mac, mail):
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
		title = "{} {}".format(type, expose)

		url = "https://www.immobilienscout24.de/expose/{}\n".format(expose)

		print "\tAdding new entry: {}\n".format(url)

		if push:
		    pushover(title, text, url)
		if mac:
		    mac_notification(title, text)
		if mail:
			mailgun(title, text, url)

		ids.write(expose+'\n')

if __name__ == '__main__':
	client()