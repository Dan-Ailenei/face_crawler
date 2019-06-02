import os
import django
from django.conf import settings as django_settings


def setup_orm():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orm.settings")
    django.setup()
    os.environ.setdefault("xdg_config_home", django_settings.BASE_DIR)

