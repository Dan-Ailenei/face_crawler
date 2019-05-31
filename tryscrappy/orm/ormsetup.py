import os
import django


def setup_orm():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orm.settings")
    django.setup()
