import datetime

from django.core.cache import cache

from lib.http import render_json
from social.models import Swiped
from social.models import Friend
from common import keys
from social.logics import return_rcmd_list
# Create your views here.
from social import logics
from swiper import config
from user.models import User
from vip.logics import need_perm
from lib.cache import rds


def get_rcmd_list(request):
    "获取推荐列表"
    user = request.user
    users = return_rcmd_list(user)
    data = [user.to_dict() for user in users]

    return render_json(data)


def like(request):
    "喜欢"
    sid = int(request.POST.get('sid'))
    # 去创建一条数据
    user = request.user
    result = logics.like(user, sid)
    rds.zincrby(keys.HOT_RANK, config.SCORE_LIKE, sid)
    return render_json({'matched': result})


@need_perm('superlike')
def superlike(request):
    "超级喜欢"
    sid = request.POST.get('sid')
    # 去创建一条数据
    user = request.user
    result = logics.superlike(user, sid)

    # 添加得分 +7分
    # 尽量避免硬编码, 把东西边的可配置,已维护
    rds.zincrby(keys.HOT_RANK, config.SCORE_SUPERLIKE, sid)
    return render_json({'matched': result})


def dislike(request):
    "不喜欢"
    sid = int(request.POST.get('sid'))
    user = request.user
    Swiped.objects.create(uid=user.id, sid=sid, mark='dislike')
    rds.zincrby(keys.HOT_RANK, config.SCORE_DISLIKE, sid)
    return render_json(None)


@need_perm('rewind')
def rewind(request):
    "反悔 (每天允许反悔 3 次)"
    user = request.user
    """永远不要相信客户端传过来的数据"""
    result = logics.rewind(user)
    return render_json({'rewinded': result})


@need_perm('show_liked_me')
def get_liked_list(request):
    """查看喜欢过我的人"""
    user = request.user
    uid_list = Swiped.like_me_list(user)
    users = User.objects.filter(id__in=uid_list)
    data = [user.to_dict() for user in users]
    return render_json(data=data)


def friends(request):
    """获取用户好友信息"""
    data = [user.to_dict() for user in request.user.friends]
    return render_json(data=data)


def hot_users(request):
    """获取前10 的热门用户
    {1: {id:2, nickname:zhangsan, ... score=500},
    2: {id:6, nickname:zhangsan, ... score=500},
    3: {id:9, nickname:zhangsan, ... score=500},
    4: {id:100, nickname:zhangsan, ... score=500}
    }
    """
    top_dict = logics.get_top_n(config.TOP_N)
    return render_json(top_dict)
