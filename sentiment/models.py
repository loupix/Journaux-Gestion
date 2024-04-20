from django.db import models

# Create your models here.

class SentimentModel(models.Model):

	polarity = models.FloatField(default=0)
	subjectivity = models.FloatField(default=0)

	createdAt = models.DateTimeField(auto_now_add=True)


	def __repr__(self):
		return "<Sentiment (neg='%s', pos='%s', neu='%s')>" % (self.pos, self.neg, self.neu)






class OpinionModel(models.Model):

	pos = models.BooleanField(default=False)
	neg = models.BooleanField(default=False)
	neu = models.BooleanField(default=True)

	createdAt = models.DateTimeField(auto_now_add=True)


	def __repr__(self):
		return "<Opinion (neg='%s', pos='%s', neu='%s')>" % (self.pos, self.neg, self.neu)
