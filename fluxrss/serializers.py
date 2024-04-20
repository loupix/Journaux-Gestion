# serializers.py

from rest_framework import serializers
from fluxrss.models import FluxRssModel
from journal.models import JournalModel
from rubrique.models import RubriqueModel



class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalModel
        fields = ('id', 'name', 'icone')


class RubriqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubriqueModel
        fields = ('id', 'title', 'level', 'parent')


class FluxRssSerializer(serializers.ModelSerializer):
    journal = JournalSerializer(many=False, required=False)
    rubrique = RubriqueSerializer(many=False, required=False)

    journal_id = serializers.IntegerField(required=False)
    rubrique_id = serializers.IntegerField(required=False)

    # pattern_url = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    # url = serializers.RegexField(regex=pattern_url, required=True)

    class Meta:
        model = FluxRssModel
        fields = ('id', 'url', 'journal_id', 'rubrique_id', 'journal', 'rubrique', 'createdAt', 'updatedAt')
        optional_fields = ['journal_id', 'rubrique_id']

    def get_rubrique(self, instance):
        rubrique = self.context.get['rubrique_id']
        return RubriqueModel.get(id=rubrique)

    def get_journal(self, instance):
        journal = self.context.get['journal_id']
        return JournalModel.get(id=journal)

