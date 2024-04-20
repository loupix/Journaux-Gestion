from django.db import models
import pandas as pd
from rubrique.models import RubriqueModel


class ExtendedEnum(models.IntegerChoices):
	@classmethod
	def list(cls):
		return list(map(lambda c: {'name':c.name, 'value':c.value}, cls))




class JournalAnalyticsManager(models.Manager):
	def periodicItems(self):
		df = pd.DataFrame(list(self.items.week().values()))
		grpe = df.groupby(pd.Grouper(key='published', axis=0, freq='3h')).id.count()
		return grpe.to_dict()




class JournalModel(models.Model):

	objects = models.Manager()
	analytics = JournalAnalyticsManager()

	class JournalOpinion(ExtendedEnum):
		DROITE = 0
		GAUCHE = 1
		CENTRE = 2
		RELIGIEUX = 3
		COMMUNISTE = 4
		EXTREMISTE = 5
		SANS_OPINION = 6



	class JournalLanguage(ExtendedEnum):
		FRENCH = 0
		ENGLISH = 1
		SPANNISH = 2
		PORTUGUES = 3
		GERMAN = 4
		ITALIAN = 5
		ARABE = 6
		HINDI = 7
		CHINESE = 8
		JAPAN = 9
		COREAN = 10
		UNKNOW = 11


	name = models.CharField(max_length=155, null=False)
	url = models.CharField(max_length=155, null=True)

	_icone = models.TextField(db_column='icone', blank=True)
	def set_icone(self, icone):self._icone = base64.b64encode(icone).decode()
	def get_icone(self):return self._icone
	icone = property(get_icone, set_icone)


	opinion = models.IntegerField(choices=JournalOpinion.choices, default=JournalOpinion.SANS_OPINION)
	language = models.IntegerField(choices=JournalLanguage.choices, default=JournalLanguage.UNKNOW)

	createdAt = models.DateTimeField(auto_now_add=True)
	updatedAt = models.DateTimeField(auto_now=True)


	@property
	def validRss(self):
		return self.rssUrls.filter(lambda r:r.is_valid)

	@property
	def rubriques(self):
		return self.rssUrls.values('rubrique')
	
	class Meta:
		db_table = "journaux"
		ordering = ['-name']

		def __str__(self) -> str:
			return self.name
