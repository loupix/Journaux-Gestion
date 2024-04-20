# serializers.py

from rest_framework import serializers
from journal.models import JournalModel

class JournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalModel
        fields = ('id', 'name', 'url', 'icone', 'language', 'opinion', 'createdAt')