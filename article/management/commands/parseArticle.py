#!/env/bin/python
# -*- coding: utf-8 -*-
import sys

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from item.models import *
from item.serializers import *
from pprint import pformat
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import csv
from PIL import Image
import validators

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen












class Command(BaseCommand):
	help = ''

	def handle(self, *args, **options):


		# get_single_item_data("https://www.lefigaro.fr/politique/assemblee-nationale-la-ministre-sarah-el-hairy-confond-opprobre-et-eau-propre-dans-l-une-de-ses-reponses-20240312")
		# sys.exit()

		results = []

		item = ItemModel.objects.last()
		page = urlopen(item.link).read()

		limit = 32767

		# Remove all HTML tags
		soup = BeautifulSoup(page, "html.parser")
		for script in soup(["script", "style"]):
			script.decompose()


		# list_of_divs = []
		# for div in soup.find_all("div"):
		# 	list_of_divs.extend(
		# 		filter(lambda t:len(t)>=125, 
		# 			list(div.stripped_strings))
		# 	)
			
		# print(pformat(list_of_divs))

		for tag in soup.find_all(['aside', 'article']):
			list_of_strings = []
			for p in tag.find_all(['h1', 'h2', 'h3', 'p']):
				list_of_strings.append({'name': p.name, 'values':
					list(filter(lambda t:len(t)>=50, 
						list(p.stripped_strings))
					)
				})

			list_of_imgs = []
			for img in tag.find_all("img"):
				for tagName, value in img.attrs.items():
					if validators.url(value) and value.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
						image = Image.open(urlopen(value))
						w, h = image.size
						list_of_imgs.append({'width':w, 'height':h, 'src':value})
			

			print(tag.name, pformat(list_of_strings))
			print(tag.name, pformat(list_of_imgs))


		

		# print(pformat(strips))

		# # Connect all pieces of textxsinto a single string
		# string = ''
		# for s in strips:
		# 	string += ' ' + s

		# # Divide the string into slices of at most 'limit' characters
		# list_of_strings = []
		# index = 0
		# while index < len(string):
		# 	end = index + limit
		# 	list_of_strings.append(string[index:end])
		# 	index += limit + 1
