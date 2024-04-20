# serializers.py

from rest_framework import serializers
from item.models import *
from journal.models import JournalModel
from rubrique.models import RubriqueModel


from datetime import datetime
from pprint import pformat







class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalModel
        fields = '__all__'



class RubriqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubriqueModel
        fields = '__all__'












class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentModel
        fields = '__all__'
        depth = 1


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaModel
        fields = '__all__'
        depth = 1


# class MediaCreditSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MediaCreditModel
#         fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagModel
        fields = '__all__'
        depth = 1















class ItemSerializer(serializers.ModelSerializer):

    journal = JournalSerializer(many=False, required=False)
    rubriques = RubriqueSerializer(many=True, required=False)

    content = ContentSerializer(many=True, required=False)
    # media_credits = MediaCreditSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    medias = MediaSerializer(many=True, required=False)

    class Meta:
        model = ItemModel
        fields = '__all__'

    def create(self, validated_data):
        return ItemModel.objects.create(**self.validated_data)


    def save(self, journal):



        tags = self.validated_data.pop('tags', [])
        medias = self.validated_data.pop('medias', [])
        rubriques = self.validated_data.pop('rubriques')
        if 'content' in self.validated_data:
            content = self.validated_data.pop('content')

        item, created = ItemModel.objects.get_or_create(**self.validated_data, journal=journal)

        rubrique = RubriqueModel.objects.filter(**rubriques[0]).first()
        if rubrique not in item.rubriques.all():
            item.rubriques.add(rubrique)
            item.save()

        if not created:return False

        if len(tags):
            for tag in tags:
                tag_obj, created = TagModel.objects.get_or_create(**tag)
                tag_obj.items.add(item)
                tag_obj.save()
                item.tags.add(tag_obj)
            item.save()

        if len(medias):
            for media in medias:
                media_obj, created = MediaModel.objects.get_or_create(**media)
                media_obj.items.add(item)
                media_obj.save()
                item.medias.add(media_obj)
            item.save()




        # contents = self.validated_data.pop('content', [])
        # if len(contents):
        #     content_objs = []
        #     for content in contents:
        #         content_obj, created = ContentModel.objects.get_or_create(item=item, base=content['base'], langage=content['langage'], value=content['value'])
        #         content_objs.append(content_obj)
        #     # item.contents.set(content_objs[0])


        return True