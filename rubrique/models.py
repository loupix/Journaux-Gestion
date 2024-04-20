from django.db import models



class RubriqueModel(models.Model):

	title = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	parent = models.IntegerField()
	level = models.IntegerField()

	# articles = models.ManyToManyField(Article)
	# rssUrls = models.ManyToManyField(FluxRss)
	# journals = models.ManyToManyField(Journal)

	# parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children')

	createdAt = models.DateTimeField(auto_now_add=True)
	updatedAt = models.DateTimeField(auto_now=True)


	class Meta:
		db_table = "rubriques"
		# ordering = ['-createdAt']

		def __str__(self) -> str:
			return self.title



	@property
	def nbArticle(self):
		return len(self.articles)

	# @property
	# def parents(self):
	# 	def getParent(rubrique, previous=[]):
	# 		if rubrique.parent != None:
	# 			previous.append(rubrique.parent)
	# 			return getParent(rubrique.parent, previous)
	# 		else:
	# 			return previous
	# 	parents = [self]
	# 	parents.extend(getParent(self))
	# 	return list(map(lambda r:r.name, reversed(parents)))

	# @property
	# def parent_id(self):
	# 	if self.parent is not None:return self.parent.json()
	# 	else: return False