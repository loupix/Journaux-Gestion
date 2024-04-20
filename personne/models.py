from django.db import models

# Create your models here.

class PersonneModel(models.Model):

	first_name = models.CharField(max_length=25)
	last_name = models.CharField(max_length=25)
	date_of_birth = models.DateTimeField(auto_now=True)
	_picture = models.TextField(db_column='picture', blank=True)
	def set_picture(self, picture):self._picture = base64.b64encode(picture).decode()
	def get_picture(self):return self._picture
	picture = property(get_picture, set_picture)

	# journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name="personnes")
	# articles = models.oneToMany(Article)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	@property
	def age(self):
		diff = datetime.now() - self.date_of_birth
		return diff.year


	def __repr__(self):
		return "<Personne (nom='%s', prenom='%s', age='%d')>" % (self.first_name, self.last_name, self.age)


