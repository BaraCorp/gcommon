#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import peewee

from datetime import datetime

from Common.models import (BaseModel, Owner, SettingsAdmin, Version,
                           FileJoin, Organization)

FDATE = u"%c"


class Store(BaseModel):

    # class Meta:
    #     order_by = ('name',)

    name = peewee.CharField(max_length=100, unique=True)
    stock_maxi = peewee.IntegerField(default=1000, null=True)

    def __str__(self):
        return self.display_name()

    def display_name(self):
        return u"{}/{}".format(self.name.title(), self.stock_maxi)


class Category(BaseModel):

    # class Meta:
    #     order_by = ('name', 'desc')

    name = peewee.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.display_name()

    def display_name(self):
        return u"{}".format(self.name)

    @classmethod
    def get_or_create(cls, name):
        try:
            ctct = cls.get(name=name)
        except cls.DoesNotExist:
            ctct = cls.create(name=name)
        return ctct


# class Product(BaseModel):
#     pass
