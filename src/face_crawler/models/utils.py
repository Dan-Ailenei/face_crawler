import datetime

from django.db.models import ManyToManyField, ForeignKey
from django.db.models.fields.files import ImageFieldFile


def person_to_dict(instance):
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.identifier is None:
                data[f.name] = []
            else:
                if f.name != 'friends':
                    data[f.name] = [(pers.identifier, pers.name) for pers in f.value_from_object(instance)]
        elif isinstance(f, ForeignKey):
            pers = getattr(instance, f.name)
            if pers:
                data[f.name] = pers.identifier, pers.name
            else:
                data[f.name] = pers
        else:
            val = f.value_from_object(instance)
            if isinstance(val, datetime.date):
                data[f.name] = str(val)
            elif not isinstance(val, ImageFieldFile):
                data[f.name] = val
    return data
