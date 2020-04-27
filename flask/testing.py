# debug.py

from app import instance, db

app = instance()
app.app_context().push()

from app.common.models import *
from app import s3

