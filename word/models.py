from django.db import models

class KeywordModel(models.Model):
	word = models.CharField(max_length=255)
	forme_gramm = models.CharField(max_length=255)
	active = models.BooleanField(default=True)

	# list_id = Column(Integer, ForeignKey('keywords_list.id'))
	# list = relationship("KeyLists")
	# liste = models.ForeignKey(KeyList, on_delete=models.CASCADE, related_name="keywords")

	# articles = models.ManyToManyField(Article)

	createdAt = models.DateTimeField(auto_now_add=True)
	updatedAt = models.DateTimeField(auto_now=True)

	def __repr__(self):
		return "<KeyWord (word='%s', active='%s'>" % (self.word, self.active)





class KeylistModel(models.Model):

	name = models.CharField(max_length=255)
	description = models.TextField()
	color = models.CharField(max_length=255, default="#fafafa")
	active = models.BooleanField(default=True)

	keywords = models.ManyToManyField(KeywordModel)

	createdAt = models.DateTimeField(auto_now_add=True)
	updatedAt = models.DateTimeField(auto_now=True)

	def __repr__(self):
		return "<KeyList (name='%s', active='%s', words='%d'>" % (self.name, self.active, len(self.words))
