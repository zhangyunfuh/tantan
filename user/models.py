import datetime

from django.db import models


# Create your models here.
from social.models import Friend
from vip.models import Vip


class User(models.Model):
    """用户模型"""
    SEX = (
        ('male', '男'),
        ('female', '女')
    )
    phonenum = models.CharField(max_length=20, unique=True, verbose_name='手机号')
    nickname = models.CharField(max_length=64, unique=True, verbose_name='昵称')
    sex = models.CharField(choices=SEX, max_length=8, verbose_name='性别')
    birth_year = models.IntegerField(default=2000, verbose_name='出生年')
    birth_month = models.IntegerField(default=1, verbose_name='出生月')
    birth_day = models.IntegerField(default=1, verbose_name='出生日')
    avatar = models.CharField(max_length=256, verbose_name='个人形象')
    location = models.CharField(max_length=8, verbose_name='常居地')

    # 和vip的关系
    vip_id = models.IntegerField(default=0, verbose_name='用户的会员id')

    class Meta:
        db_table = 'users'

    @property
    def age(self):
        today = datetime.date.today()
        birthday = datetime.date(year=self.birth_year, month=self.birth_month, day=self.birth_day)
        return (today - birthday).days // 365

    @property
    def profile(self):
        if not hasattr(self, '_profile'):
            self._profile, _ = Profile.get_or_create(id=self.id)
        return self._profile

    @property
    def vip(self):
        """获取用户的vip"""
        if not hasattr(self, '_vip'):
            self._vip = Vip.get(id=self.vip_id)
        return self._vip

    @property
    def friends(self):
        """返回用户的好友"""
        friends_list = Friend.get_friends_list(self)
        users = User.objects.filter(id__in=friends_list)
        return users

    def to_dict(self):
        return {
            "id": self.id,
            "phonenum": self.phonenum,
            "nickname": self.nickname,
            "sex": self.sex,
            "age": self.age,
            "avatar": self.avatar,
            "location": self.location,
        }


class Profile(models.Model):
    """个人资料"""
    SEX = (
        ('male', '男'),
        ('female', '女')
    )
    location = models.CharField(max_length=20, verbose_name='目标城市')
    min_distance = models.IntegerField(default=0,verbose_name='最小查找范围')
    max_distance = models.IntegerField(default=50, verbose_name='最大查找范围')
    min_dating_age = models.IntegerField(default=18, verbose_name='最小交友年龄')
    max_dating_age = models.IntegerField(default=50, verbose_name='最大交友年龄')
    dating_sex = models.CharField(max_length=8, choices=SEX, verbose_name='匹配的性别')
    vibration = models.BooleanField(default=True, verbose_name='开启震动')
    only_matche = models.BooleanField(default=True, verbose_name='不让为匹配的人看我的相册')
    auto_play = models.BooleanField(default=True, verbose_name='自动播放视频')
