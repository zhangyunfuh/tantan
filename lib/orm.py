"""封装to_dict"""
from django.db import models
from django.core.cache import cache



def to_dict(self):
    att_dict = {}
    for field in self._meta.get_fields():
        att_dict[field.attname] = getattr(self, field.attname)
    return att_dict

# 只对pk和id的查询做缓存
@classmethod
def get(cls, *args, **kwargs):
    # 从缓存中获取对象.
    # 对用的最多的pk和id做一个缓存.
    # 先把pk或者id从kwargs找出来.
    pk = kwargs.get('pk') or kwargs.get('id')
    if pk is not None:
        key = '%s-%s' % (cls.__name__, pk)
        model_obj = cache.get(key)
        if model_obj is None:
            model_obj = cls.get(*args, **kwargs)
            cache.set(key, model_obj, 86400 * 14)
        return model_obj

    model_obj = cls.get(*args, **kwargs)
    return model_obj


@classmethod
def get_or_create(cls, *args, **kwargs):
    # 从缓存中获取对象.
    # 对用的最多的pk和id做一个缓存.
    # 先把pk或者id从kwargs找出来.
    pk = kwargs.get('pk') or kwargs.get('id')
    if pk is not None:
        key = '%s-%s' % (cls.__name__, pk)
        model_obj = cache.get(key)
        if model_obj is None:
            model_obj = cls.objects.get_or_create(*args, **kwargs)
            cache.set(key, model_obj, 86400 * 14)
        return model_obj

    model_obj = cls.objects.get_or_create(*args, **kwargs)
    return model_obj


def save(self, force_insert=False, force_update=False, using=None,
         update_fields=None):
    # 只需要更新缓存的数据
    key = '%s-%s' % (self.__class__.__name__, self.pk)
    cache.set(key, self, 86400 * 14)
    self._origin_save(force_insert=False, force_update=False, using=None,
         update_fields=None)


def model_patch():
    # 给model增加方法.
    models.Model.get = get
    models.Model.to_dict = to_dict
    models.Model.get_or_create = get_or_create

    # 修改原生的save
    models.Model._origin_save = models.Model.save
    models.Model.save = save
