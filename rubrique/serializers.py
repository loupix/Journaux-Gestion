# serializers.py

from rest_framework import serializers
from rubrique.models import RubriqueModel
from fluxrss.models import FluxRssModel
from journal.models import JournalModel



class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalModel
        fields = ('id', 'title')


class RubriqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubriqueModel
        fields = ('id', 'title', 'parent', 'level')
        optional_fields = ['description', 'updatedAt']
