from django.db import models
from django.db.models import Q
# Create your models here.


class Swiped(models.Model):
    MARKS = (
        ('dislike', '左滑'),
        ('like', '右滑'),
        ('superlike', '超级喜欢')
    )
    uid = models.IntegerField(verbose_name='滑动者id')
    sid = models.IntegerField(verbose_name='被滑者id')
    mark = models.CharField(max_length=20, choices=MARKS, verbose_name='滑动的类型')
    stime = models.DateTimeField(auto_now_add=True, verbose_name='滑动时间')

    @classmethod
    def like(cls, user, sid):
        return Swiped.objects.create(uid=user.id, sid=sid, mark='like')

    @classmethod
    def superlike(cls, user, sid):
        return Swiped.objects.create(uid=user.id, sid=sid, mark='superlike')

    @classmethod
    def has_liked_someone(cls, user, sid):
        return Swiped.objects.filter(uid=sid, sid=user.id,
                              mark__in=['like', 'superlike']).exists()
    @classmethod
    def like_me_list(cls, user):
        swiped = cls.objects.filter(sid=user.id,
                                       mark__in=['like', 'superlike']).only('uid')
        uid_list = [sw.uid for sw in swiped]
        return uid_list

class Friend(models.Model):
    """好友表"""
    uid1 = models.IntegerField()
    uid2 = models.IntegerField()

    @classmethod
    def make_friends(cls, uid, sid):
        uid1, uid2 = (uid, sid) if uid < sid else (sid, uid)
        Friend.objects.create(uid1=uid1, uid2=uid2)
        return True

    @classmethod
    def get_friends_list(cls, user):
        friends_list = []
        friends = cls.objects.filter(Q(uid1=user.id) | Q(uid2=user.id))
        # [sid = uid1 if uid2 == user.id else uid2]
        for friend in friends:
            if friend.uid1 == user.id:
                friends_list.append(friend.uid2)
            else:
                friends_list.append(friend.uid1)
        return friends_list


    def __str__(self):
        return f'{self.uid1}, {self.uid2}'
