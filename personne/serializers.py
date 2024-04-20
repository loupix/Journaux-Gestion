# serializers.py

from rest_framework import serializers
from personne.models import PersonneModel

class PersonneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonneModel
        fields = ('first_name', 'last_name', 'age', 'picture')