from django.db import models

# Create your models here.
"""
人和vip的关系  一对多的关系
vip和权限的关系 对多多的关系.


vip1 白金会员
   查看喜欢我的人
   
   
vip2 钻石会员
    查看喜欢我的人
    超级喜欢
    
vip3 至尊会员
    查看喜欢我的人
    超级喜欢
    反悔
"""

class Vip(models.Model):
    """vip表"""
    name = models.CharField(max_length=32, unique=True, verbose_name='vip名称')
    level = models.IntegerField(default=1, verbose_name='会员等级')
    price = models.FloatField(verbose_name='会员价格')

    @property
    def perms(self):
        """获取当前vip的所有权限"""
        relation = VipPermRelation.objects.filter(vip_id=self.id).only('perm_id')
        perm_id_list = [rel.perm_id for rel in relation]
        perms = Permission.objects.filter(id__in=perm_id_list)
        return perms


    def has_perm(self, perm_name):
        """判断当前vip是否具有某个权限"""
        for perm in self.perms:
            if perm.name == perm_name:
                return True
        return False

    def __str__(self):
        return '会员{} {}'.format(self.id, self.name)


class Permission(models.Model):
    """权限表"""
    name = models.CharField(max_length=32, unique=True, verbose_name='权限名称')
    description = models.TextField(verbose_name='权限描述')

    def __str__(self):
        return self.name


class VipPermRelation(models.Model):
    """vip和权限关系表"""
    vip_id = models.IntegerField(verbose_name='vip的id')
    perm_id = models.IntegerField(verbose_name='权限的id')


