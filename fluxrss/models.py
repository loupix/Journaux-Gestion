import sys, os, json, math, re, base64, ssl
import urllib.request
from random import choice

from django.db import models
from journal.models import JournalModel
from rubrique.models import RubriqueModel


class FluxRssManager(models.Manager):
	def valid(self):
		return self.filter(is_valid=True).all()

class ValidFluxRss(models.Model):
	def get_queryset(self):
		return super().get_queryset().filter(is_valid=True)

class FluxRssModel(models.Model):

	objects = FluxRssManager()
	valid = ValidFluxRss()

	url = models.CharField(max_length=255, null=False, unique=True)
	is_valid = models.BooleanField(default=False)

	journal = models.ForeignKey(JournalModel, on_delete=models.CASCADE, related_name="rssUrls")
	rubrique = models.ForeignKey(RubriqueModel, on_delete=models.CASCADE, related_name="rssUrls")

	createdAt = models.DateTimeField(auto_now_add=True)
	updatedAt = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "fluxrss"
		ordering = ['-createdAt']

		def __str__(self) -> str:
			return f'{self.rubrique} {self.url}'


	@property
	def check_valid(self):
		try:
			user_agents = [
				'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
				'Opera/9.25 (Windows NT 5.1; U; en)',
				'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
				'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
				'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
				'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
			]
			headers = {'User-Agent':choice(user_agents)}
			context = ssl._create_unverified_context()
			req = urllib.request.Request(self.url, headers=headers)
			res = urllib.request.urlopen(req, context=context)
			if res.getcode() != 200:
				self.is_valid=False
				return False

			http_message = res.info()
			full = http_message['Content-Type'].split(";")[0]
			types = ['application/rss+xml','application/rdf+xml','application/atom+xml','application/xml','text/xml']

			if full in types:self.is_valid=True
			else:self.is_valid=False

			return full in types
		except Exception as e:
			self.is_valid=False
			raise e


