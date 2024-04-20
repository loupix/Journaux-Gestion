# article/serializers.py

from rest_framework import serializers
from article.models import *
from item.models import ItemModel
from item.serializers import ItemSerializer




class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagModel
        fields = ('name','values')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ('width','height','url')


class ArticleSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False, required=True)
    tags = TagSerializer(many=True, required=True)
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = ArticleModel
        fields = '__all__'

    def save(self):

        item = self.validated_data.pop('item')
        tags = self.validated_data.pop('tags', [])
        images = self.validated_data.pop('images', [])

        item_obj = ItemModel.objects.filter(**item).first()
        article, created = ArticleModel.objects.get_or_create(**self.validated_data, item=item_obj)

        if len(tags):
            for tag in tags:
                tag_obj, created = TagModel.objects.get_or_create(**tag, article=article)
                article.tags.add(tag_obj)
            article.save()

        if len(images):
            for image in images:
                image_obj, created = ImageModel.objects.get_or_create(**image, article=article)
                article.images.add(image_obj)
            article.save()


        return True

