import datetime

from django.core.cache import cache

from lib.cache import rds
from social.models import Swiped, Friend
from user.models import User
from common import keys
from swiper import config
from common import errors


def return_rcmd_list(user):
    """从数据库中选择一些用户来推荐"""
    # 找出被滑过的用户 .
    swiped = Swiped.objects.filter(uid=user.id).only('sid')
    swiped_sid_list = [sw.id for sw in swiped]

    # 把自己排出.
    swiped_sid_list.append(user.id)

    curr_year = datetime.date.today().year
    min_birth_year = curr_year - user.profile.max_dating_age
    max_birth_year = curr_year - user.profile.min_dating_age

    users = User.objects.filter(
        location=user.profile.location,
        sex=user.profile.dating_sex,
        birth_year__range=[min_birth_year, max_birth_year]
    ).exclude(id__in=swiped_sid_list)[:20]

    return users


def like(user, sid):
    Swiped.like(user, sid)
    # 判断一下自己是否被对方喜欢过.
    if Swiped.has_liked_someone(user, sid):
        # 如果喜欢过就建立好友关系.
        return Friend.make_friends(user.id, sid)
        # TODO:通知对方好友关系已经建立,可以聊天了.
    else:
        return False


def superlike(user, sid):
    Swiped.superlike(user, sid)
    # 判断一下自己是否被对方喜欢过.
    if Swiped.has_liked_someone(user, sid):
        # 如果喜欢过就建立好友关系.
        return Friend.make_friends(user.id, sid)
        # TODO:通知对方好友关系已经建立,可以聊天了.
    else:
        return False


def rewind(user):
    now = datetime.datetime.now()
    key = keys.REWIND_KEY % (user.id, now.date())
    # 获取当天的已反悔次数
    rewind_times = cache.get(key, 0)
    # 检查反悔次数是否已经超过限制.
    if rewind_times < config.REWIND_TIMES:
        #  如果没超过,可以反悔
        #  反悔次数加1
        rewind_times += 1
        # 计算当天剩下的秒数
        timeout = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
        cache.set(key, rewind_times, timeout)
        record = Swiped.objects.filter(uid=user.id).latest('stime')
        # 反悔之后也要取消好友关系.
        uid1, uid2 = (user.id, record.sid) if user.id < record.sid else (record.sid, user.id)
        # print(uid1, uid2)
        relation = Friend.objects.filter(uid1=uid1, uid2=uid2)
        # print(relation)
        relation.delete()


        # 处理热度得分
        # if record.mark == 'like':
        #     rds.zincrby(keys.HOT_RANK, -config.SCORE_LIKE, record.sid)
        # elif record.mark == 'superlike':
        #     rds.zincrby(keys.HOT_RANK, -config.SCORE_SUPERLIKE, record.sid)
        # else:
        #     rds.zincrby(keys.HOT_RANK, -config.SCORE_DISLIKE
        #                 , record.sid)
        # 利用字典做模式匹配.
        score_mapping = {
            'like': config.SCORE_LIKE,
            'superlike': config.SCORE_SUPERLIKE,
            'dislike': config.SCORE_DISLIKE
        }
        rds.zincrby(keys.HOT_RANK, -score_mapping[record.mark], record.sid)

        record.delete()
        return True
    else:
        raise  errors.RewindLimit('已超过最大反悔次数')  # 实际应该返回一个状态码.


def get_top_n(num):
    # 从redis缓存中拿数据
    # [[b'184', 7.0], [b'183', 7.0], [b'15', 7.0], [b'188', 5.0], [b'128', 5.0]]
    origin_data = rds.zrevrange('HOT_RANK', 0, num - 1, withscores=True)
    # 对redis中的数据进行简单清洗
    # [(184, 7), (183, 7), (15, 7), (188, 5), (128, 5)]
    cleaned_data = [(int(id), int(score)) for id, score in origin_data]
    # 以下代码性能低下.for每次循环都会访问数据库.
    # users = []
    # for uid,_ in cleaned_data:
    #     users.append(User.get(id=uid))
    # [184, 183, 15, 188, 128]
    uid_list = [uid for uid, _ in cleaned_data]
    # queryset 默认是按照id的升序进行排列.
    users = User.objects.filter(id__in=uid_list)
    users = sorted(users, key=lambda user: uid_list.index(user.id))

    top_dict = {}
    for rank, (_, score), user in zip(range(1, num+1), cleaned_data, users):
        user_attr = user.to_dict()
        user_attr['score'] = score
        top_dict[rank] = user_attr
    return top_dict






