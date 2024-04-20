from django.db import models

from item.models import ItemModel
from personne.models import PersonneModel
from word.models import KeywordModel
from sentiment.models import SentimentModel, OpinionModel

try:
   import cPickle as pickle
except:
   import pickle


class ExtendedEnum(models.IntegerChoices):
	@classmethod
	def list(cls):
		return list(map(lambda c: {'name':c.name, 'value':c.value}, cls))




class ArticleModel(models.Model):


	item = models.ForeignKey(ItemModel, on_delete=models.CASCADE, related_name="articles", null=False)

	# keywords = models.ManyToManyField(KeywordModel)
	# personnes = models.ManyToManyField(PersonneModel)

	# sentiment = models.ForeignKey(SentimentModel, on_delete=models.CASCADE, related_name="articles", null=True)
	# opinion = models.ForeignKey(OpinionModel, on_delete=models.CASCADE, related_name="articles", null=True)


	createdAt = models.DateTimeField(auto_now_add=True)


	@property
	def contentHtml(self):
		return

	class Meta:
		db_table = "articles"
		ordering = ['-createdAt']

		def __str__(self) -> str:
			return self.contentHtml






class TagModel(models.Model):
	name = models.CharField(max_length=5)
	value = models.TextField()
	article = models.ForeignKey(ArticleModel, on_delete=models.CASCADE, related_name="tags")

	def set_values(self, values):self.value = pickle.dumps(values)
	def get_values(self):return pickle.loads(self.value)
	values = property(get_values, set_values)


	class Meta:
		db_table = "articles_tags"
		def __str__(self) -> str:
			return self.name







class ImageModel(models.Model):

	width = models.IntegerField()
	height = models.IntegerField()
	url = models.TextField()
	article = models.ForeignKey(ArticleModel, on_delete=models.CASCADE, related_name="images")

	class Meta:
		db_table = "articles_images"
		def __str__(self) -> str:
			return self.url

