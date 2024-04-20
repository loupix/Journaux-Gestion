#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from journal.models import JournalModel
from item.models import *
from item.serializers import *
import pandas as pd
from pprint import pformat
from datetime import datetime, timedelta




class Command(BaseCommand):
	help = ''

	def handle(self, *args, **options):


		journal = JournalModel.objects.last()
		df = pd.DataFrame(list(journal.items.week().values()))
		grpe = df.groupby(pd.Grouper(key='published', axis=0, freq='3h')).title.count()
		periodic = [{'time':t.strftime("%c"), 'value':v} for t, v in grpe.to_dict().items()]
		print(pformat(periodic))

		all_tags = list()
		for item in journal.items.week():
			all_tags.extend(item.tags.values_list('term'))

		df = pd.DataFrame(list(all_tags))
		print(df[0].value_counts())
