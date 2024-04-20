#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import sys
from pprint import pformat
import socket, threading
import dispy
from datetime import datetime
from journal.models import JournalModel
from item.serializers import ItemSerializer
from article.models import *
from article.serializers import *



import logging
logger = logging.getLogger("commands")

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



rpi_name = {"node%s" % i:"node%s.lan" % i for i in range(5,15)}
rpi_name.update({"serv%s" % i:"serv%s.lan" % i for i in range(1,3)})

rpi_ip = {k:socket.gethostbyname(ns) for k, ns in rpi_name.items()}
rpi_final = {}

detectors = {}


serializer_article = ArticleSerializer
serializer_image = ImageSerializer
serializer_tag = TagSerializer






def check_port(name:str, ip:str, port:int) -> None :
	global rpi_final
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
		#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		socket.setdefaulttimeout(2.0) # seconds (float)
		result = sock.connect_ex((ip,port))
		if result == 0:
			# print ("Port is open")
			rpi_final[name] = "OPEN"
		else:
			# print ("Port is closed/filtered")
			rpi_final[name] = "CLOSED"
		sock.close()
	except Exception as e:
		print(e)
		pass



def get_cluster_nodes(port:int=9701) -> list:
	global rpi_ip, rpi_final

	def status_is_open(pair):
		name, status = pair
		return status=="OPEN"

	threads = []
	for name, ip in list(rpi_ip.items()):
		t = threading.Thread(target=check_port, args=[name, str(ip), port])
		t.start()
		threads.append(t)
	for t in threads:t.join()

	rpi_final = dict(filter(status_is_open, rpi_final.items()))
	cluster_nodes = [rpi_ip[name] for name in rpi_final.keys()]
	return cluster_nodes










####     In-memory Processing    ####




def setup() -> bool:
	global urlopen, BeautifulSoup, Image, validators
	import sys, os
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	sys.path.append('../')

	from bs4 import BeautifulSoup
	from PIL import Image
	import validators

	try:
		# For Python 3.0 and later
		from urllib.request import urlopen
	except ImportError:
		# Fall back to Python 2's urllib2
		from urllib2 import urlopen




	# from textblob import Blobber
	# from textblob_fr import PatternTagger, PatternAnalyzer


	return 0


def cleanup() -> None:
	global urlopen, BeautifulSoup, Image, validators
	if os.name != 'nt':
		del urlopen, BeautifulSoup, Image, validators








def compute(url, item):

	page = urlopen(url).read()
	soup = BeautifulSoup(page, "html.parser")

	list_of_articles = []

	try:
		for tag in soup.find_all('article'):
			list_of_tags = []
			try:
				for p in tag.find_all(['h1', 'h2', 'h3', 'p']):
					if(len(list(p.stripped_strings))<50):continue
					list_of_tags.append({'name': p.name, 'values':list(p.stripped_strings)})

					# values = list(filter(lambda t:len(t)>=50,
					# 	list(p.stripped_strings))
					# )
					# if(len(values)):
					# 	list_of_tags.append({'name': p.name, 'value':values.join()})
			except Exception as e:
				raise e

			list_of_images = []
			try:
				for img in tag.find_all("img"):
					for tagName, value in img.attrs.items():
						if validators.url(value) and value.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
							image = Image.open(urlopen(value))
							w, h = image.size
							list_of_images.append({'width':w, 'height':h, 'url':value})
			except Exception as e:
				raise e

			list_of_articles.append({'tags':list_of_tags, 'images':list_of_images, 'item':item})


		return dispy_node_name, list_of_articles
	except Exception as error:
		return error








#############   Initialisation du Cluster   ###################





def parseArticles(cluster):

	global logger

	now = datetime.now()
	jobs = []

	for journal in JournalModel.objects.all():
		jobNow = datetime.now()
		jobs = []
		nSuccess, nbSaved, nbItems, nbError = 0, 0, 0, 0
		items = journal.items.day()
		logger.info("%s  %d items" % (journal.name, len(items)))
		for item in items:
			job = cluster.submit(item.link, ItemSerializer(item).data)
			jobs.append(job)

		for job in jobs:
			list_of_articles = []
			try:
				host, list_of_articles = job()
				nSuccess+=1
				logger.debug('job %s - (%s %s) ' % (job.id, host, job.ip_addr))
			except ValueError as e:
				nbError+=1
				logger.error("Value error %s (%s %s) : %s - %s" % (job.id, host, job.ip_addr, job(), e))
				print(pformat(job()))
				continue
			except Exception as error:
				nbError+=1
				logger.error("Error job %s (%s) - %s : %s" % (job.id, job.ip_addr, journal.name, error))
				print(pformat(job()))
				continue

			for article in list_of_articles:
				serializer = serializer_article(data=article)
				if serializer.is_valid():
					try:
						if serializer.save():
							nbSaved += 1
					except Exception as error:
						logger.error(error)
					finally:pass
				else:logger.error(pformat(serializer.errors))

				nbItems += 1

			logger.info("%d/%d jobs en %s - %d/%d Saved - %d Errors" 
				% (nSuccess, len(jobs), datetime.now() - jobNow, nbSaved, nbItems, nbError)
			)












########  Running Command #############


class Command(BaseCommand):
	help = ''

	def handle(self, *args, **options):

		logger.info("Check Cluster Ports")
		cluster_nodes = get_cluster_nodes()
		if len(cluster_nodes)==0:raise Exception("Aucuns noeuds")

		logger.info("%d nodes" % len(cluster_nodes))
		nodes = [dispy.NodeAllocate(ip, cpus=3) for ip in cluster_nodes]


		logger.info("Initialize Cluster")
		cluster = dispy.JobCluster(compute, nodes=nodes, setup=setup, cleanup=cleanup, 
			recover_file="dispy_articles_log",  loglevel=dispy.logger.INFO)


		logger.info("Running Cluster Computation")
		parseArticles(cluster)

		logger.info("Close Cluster")
		cluster.close()
