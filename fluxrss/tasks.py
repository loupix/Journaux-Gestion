# fluxrss/tasks.py
import os, sys, re

from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timezone import utc

from fluxrss.models import FluxRssModel
from journal.models import JournalModel
from rubrique.models import RubriqueModel

from journauxGestion.celery import app


@app.task
def xsum(numbers):
    return sum(numbers)
