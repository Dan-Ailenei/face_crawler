from django.db import models


class Person(models.Model):
    identifier = models.CharField(max_length=60, primary_key=True)
    picture = models.ImageField(null=True)
    friends = models.ManyToManyField('Person')

    brothers = models.ManyToManyField('Person', related_name='%(class)s_brothers')
    sisters = models.ManyToManyField('Person', related_name='%(class)s_sisters')
    mother = models.ForeignKey('Person', on_delete=models.SET_NULL, related_name='%(class)s_mother', null=True)
    father = models.ForeignKey('Person', on_delete=models.SET_NULL, related_name='%(class)s_father', null=True)

    name = models.CharField(max_length=60)
    birthday = models.DateField(null=True)
    sex = models.BooleanField(null=True)
    country = models.CharField(null=True, max_length=50)

    scraped = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.identifier} Name:{self.name} Birthday:{self.birthday} Sex:{self.sex} Scrapped:{self.scraped}'

    def __eq__(self, other):
        return self.identifier == other.identifier

    def add_to_friends(self, op):
        self.friends.add(op)
        op.friends.add(self)
