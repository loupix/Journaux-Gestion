from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
from journal.models import JournalModel
from rubrique.models import RubriqueModel
from personne.models import PersonneModel




class ItemManager(models.Manager):

	def hours(self, hour=3):
		return self.filter(published__gte=datetime.now(tz=timezone.utc) - timedelta(hours=hour))

	def day(self):
		return self.filter(published__gte=datetime.now(tz=timezone.utc) - timedelta(hours=24))

	def week(self):
		return self.filter(published__gte=datetime.now(tz=timezone.utc) - timedelta(days=7))

	def month(self):
		return self.filter(published__gte=datetime.now(tz=timezone.utc) - timedelta(months=1))




class ItemModel(models.Model):

	objects = ItemManager()

	title = models.CharField(max_length=255)
	summary = models.TextField(null=True, blank=True)
	link = models.CharField(max_length=1024)

	credit = models.CharField(max_length=255, null=True, blank=True)
	source = models.CharField(max_length=255, null=True, blank=True)
	author = models.CharField(max_length=255, null=True, blank=True)
	license = models.CharField(max_length=255, null=True, blank=True)

	created = models.DateTimeField(null=True)
	published = models.DateTimeField(null=True)
	expired = models.DateTimeField(null=True)
	updated = models.DateTimeField(null=True)


	journal = models.ForeignKey(JournalModel, on_delete=models.CASCADE, related_name="items")
	rubriques = models.ManyToManyField(RubriqueModel, related_name="items")
	auteur = models.ForeignKey(PersonneModel, on_delete=models.CASCADE, related_name="items", null=True)


	created_at = models.DateTimeField(auto_now_add=True)


	class Meta:
		db_table = "items"
		ordering = ['-published']

		def __str__(self) -> str:
			return self.title

	@property
	def credits(self):
		return self.credits.all()


	@property
	def medias(self):
		return self.medias.all()


	@property
	def tags(self):
		return self.tags.all()
	










class ContentModel(models.Model):


	base = models.CharField(max_length=255, blank=True, null=True)
	langage = models.CharField(max_length=15, null=True)
	value = models.TextField(blank=True, null=True)

	item = models.ForeignKey(ItemModel, on_delete=models.CASCADE, related_name="content")

	created_at = models.DateTimeField(auto_now_add=True)


	class Meta:
		db_table = "items_content"
		def __str__(self) -> str:
			return self.term





# class MediaCreditModel(models.Model):


# 	content = models.CharField(max_length=255, unique=True)

# 	items = models.ManyToManyField(ItemModel, related_name="media_credit")

# 	created_at = models.DateTimeField(auto_now_add=True)


# 	class Meta:
# 		db_table = "items_credit"
# 		def __str__(self) -> str:
# 			return self.term






class MediaModel(models.Model):

	width = models.IntegerField()
	height = models.IntegerField()
	url = models.TextField()

	items = models.ManyToManyField(ItemModel, related_name="medias")

	created_at = models.DateTimeField(auto_now_add=True)


	class Meta:
		db_table = "items_medias"
		def __str__(self) -> str:
			return self.url






class TagAnalyticsManager(models.Manager):
	def number_of_items(self):
		return self.aggregate(
			count=models.Count("items")
		)['count']

	def periodicItems(self, nbDays=7):
		df = pd.DataFrame(list(self.items.month()))
		grpe = df.groupby(pd.Grouper(key='published', axis=0, freq='3h')).title.count()
		return grpe.to_dict()






class TagModel(models.Model):

	objects = models.Manager()
	analytics = TagAnalyticsManager()

	label = models.CharField(max_length=255, null=True)
	scheme = models.CharField(max_length=255, null=True)
	term = models.CharField(max_length=255)

	items = models.ManyToManyField(ItemModel, related_name="tags")

	created_at = models.DateTimeField(auto_now_add=True)


	class Meta:
		db_table = "items_tags"
		def __str__(self) -> str:
			return self.term


