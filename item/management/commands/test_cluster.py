#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from pprint import pformat

import socket, threading
import dispy



import feedparser
from random import choice
from datetime import datetime
from time import mktime
import multiprocessing



from django.core.management.base import BaseCommand, CommandError
from journal.models import JournalModel
from item.models import *
from item.serializers import *



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

serializer_item = ItemSerializer
serializer_media = MediaSerializer
serializer_tag = TagSerializer
serializer_content = ContentSerializer








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
	global urllib, ssl, feedparser, choice, Blobber, PatternTagger, PatternAnalyzer
	import sys, os
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	sys.path.append('../')

	import urllib
	import ssl
	import feedparser
	from random import choice


	# from textblob import Blobber
	# from textblob_fr import PatternTagger, PatternAnalyzer


	return 0


def cleanup() -> None:
	global urllib, ssl, feedparser, choice, Blobber, PatternTagger, PatternAnalyzer
	if os.name != 'nt':
		del urllib, ssl, feedparser, choice







def compute(url, rubrique):

	user_agents = [
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
		'Opera/9.25 (Windows NT 5.1; U; en)',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
		'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
		'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
		'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
	]

	try:
		# meta = MetaData()
		# engine = create_engine('postgresql://postgres:lolo@serv1:5432/socialnetwork_journaux', echo=False)
		# Session = sessionmaker(bind=engine)

		# session = Session()

		# return (dispy_node_name, url)

		# journal = Journal.objects.filter(id=journal_id).first()			

		headers = {'User-Agent':choice(user_agents)}
		context = ssl._create_unverified_context()
		req = urllib.request.Request(url, headers=headers)
		res = urllib.request.urlopen(req, context=context)

		http_message = res.info()
		full = http_message['Content-Type'].split(";")[0]
		types = ['application/rss+xml','application/rdf+xml','application/atom+xml','application/xml','text/xml']

		if full not in types:
			raise Exception("Not Valid Url")


		rawdata = res.read()
		rss = feedparser.parse(rawdata)

		for i in range(len(rss['entries'])):rss['entries'][i]['rubriques']=[rubrique]



		# tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())

		# for article in rss['entries']:
		# 	txt = ""

		# 	if 'title' in article and article['title'] != "":txt +=" %s" % article['title']
		# 	if 'description' in article and article['description'] != "":txt +=" %s" % article['description']
		# 	if 'summary' in article and article['summary'] != "":txt +=" %s" % article['summary']
		# 	if 'content' in article and article['content'] != "":txt +=" %s" % article['content']
		# 	blob = tb(txt)
		# 	article['sentiment'] = blob.sentiment

		return dispy_node_name, rss


	except Exception as error:
		return error






logger.info("Check Cluster Ports")
cluster_nodes = get_cluster_nodes()
if len(cluster_nodes)==0:raise Exception("Aucuns noeuds")

logger.info("%d nodes" % len(cluster_nodes))
nodes = [dispy.NodeAllocate(ip, cpus=3) for ip in cluster_nodes]


logger.info("Initialize Cluster")
cluster = dispy.JobCluster(compute, nodes=nodes, setup=setup, cleanup=cleanup, 
	recover_file="dispy_items.log",  loglevel=dispy.logger.DEBUG)





def runningCluster():

	global cluster, logger

	def DelDoublons(allEntries):
		all_ids, all_entries = [], {}
		for entrie in allEntries:
			if entrie['id'] in all_ids:
				all_entries[entrie['id']]['tags'].extend(entrie['tags'])
				all_entries[entrie['id']]['media_content'].extend(entrie['media_content'])
			else:
				all_ids.append(entrie['id'])
				all_entries[entrie['id']] = entrie
		return all_entries.values()



	now = datetime.now()
	jobs = []

	
	for journal in JournalModel.objects.all():
		jobNow = datetime.now()
		if journal.rubriques.count()>0:
			jobs = []
			nSuccess, nbSaved, nbItems, nbError = 0, 0, 0, 0
			try:
				if journal.rssUrls.count()>0:
					logger.info("%s  %d urls" % (journal.name, journal.rssUrls.all().count()))


					for rss in journal.rssUrls.all():
						try:
							if not rss.check_valid:
								rss.update(is_valid = False).save()
								continue
							else:
								if not rss.is_valid:
									rss.update(is_valid = True).save()

						except Exception as e:
							logger.warning(e)
							continue

						if rss.rubrique is None:continue
						if not rss.is_valid:continue
						job = cluster.submit(rss.url, RubriqueSerializer(rss.rubrique).data)
						jobs.append(job)




					#  Resultat des jobs  ##



					allEntries = []
					for job in jobs:
						try:
							host, rss = job()
							allEntries.extend(rss['entries'])
							nSuccess+=1
							logger.debug('job %s - (%s %s) ' % (job.id, host, job.ip_addr))
						except ValueError as e:
							nbError+=1
							logger.error("Value error %s (%s %s) : %s - %s" % (job.id, host, job.ip_addr, job(), e))
						except Exception as error:
							nbError+=1
							logger.error("Error job %s (%s) - %s : %s" % (job.id, job.ip_addr, journal.name, error))

					# allEntries = DelDoublons(allEntries)
					for entrie in allEntries:
						# print(pformat(entrie))
						# continue

						if 'published' in entrie:
							entrie['published'] = datetime.fromtimestamp(mktime(entrie['published_parsed']))
						if 'updated' in entrie:
							entrie['updated'] = datetime.strptime(entrie['updated'].replace("GMT","+0000"), "%a, %d %b %Y %H:%M:%S %z")
						if 'expired' in entrie:
							entrie['expired'] = datetime.strptime(entrie['expired'].replace("GMT","+0000"), "%a, %d %b %Y %H:%M:%S %z")


						if 'media_content' in entrie:
							entrie['medias'] = entrie['media_content']


						serializer = serializer_item(data=entrie)

						if not serializer.is_valid():
							logger.error(pformat(serializer.errors))
						if serializer.is_valid():
							try:
								if serializer.save(journal=journal):
									nbSaved += 1
									logger.debug("%d jobs en %s (%s) - %d Success - %d/%d Saved - %d Errors" 
										% (len(jobs), datetime.now() - jobNow, datetime.now() - now, nSuccess, nbSaved, nbItems, nbError)
									)
							except Exception as error:
								logger.error(error)
							finally:pass

						nbItems += 1

					logger.info("%d jobs en %s (%s) - %d Success - %d/%d Saved - %d Errors" 
						% (len(jobs), datetime.now() - jobNow, datetime.now() - now, nSuccess, nbSaved, nbItems, nbError)
					)
			except Exception as error:
				logger.critical("Erreur Global - %s : %s" % (journal.name, error))
			finally:
				pass












class Command(BaseCommand):
	help = ''

	def handle(self, *args, **options):
		now = datetime.now()

		# logger.info("Check Cluster Ports")
		# cluster_nodes = get_cluster_nodes()
		# if len(cluster_nodes)==0:raise Exception("Aucuns noeuds")
		# logger.info("%d nodes" % len(cluster_nodes))

		# from pprint import pprint
		# pprint(cluster_nodes)
		
		logger.info("Running Cluster Computation")
		runningCluster()


		return