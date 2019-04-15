import logging

from django.core.cache import cache

from lib.sms import send_sms
from lib.http import render_json
from common import keys
from common import errors
from user.models import User
from user.forms import ProfileForm
from user.logics import handle_upload_avatar

# Create your views here.
logger = logging.getLogger('inf')


def submit_phone(request):
    """先提交手机号码"""
    phonenum = request.POST.get('phone')
    # 拿到手机号码应该去发短信.
    send_sms.delay(phonenum)
    return render_json(None)


def submit_vcode(request):
    """获取验证登录注册"""
    phonenum = request.POST.get('phone')
    vcode = request.POST.get('vcode')
    # 判断发送的短信验证和获取的短信验证码是否一致.
    # 从缓存中取出验证码
    cached_vcode = cache.get(keys.VCODE_KEY % phonenum)
    print(cached_vcode)
    if vcode == cached_vcode:
        # 登录或注册
        # 得判断是登录还是注册.
        # 如果能从数据库中查询到这个用户,那么就说明注册过.说明操作是 登录操作.
        # try:
        #     user = User.get(phonenum=phonenum)
        # except User.DoesNotExist:
        #     # 注册
        #     user = User.objects.create(phonenum=phonenum)

        # 简化一下
        user, created = User.get_or_create(phonenum=phonenum, nickname=phonenum)
        # 登录
        request.session['uid'] = user.id
        # 用户登录成功,记录日志.
        logger.info(f'User {user.id}, login')
        return render_json(data=user.to_dict())
    else:
        raise errors.VcodeErr('验证码错误')


def get_profile(request):
    """"获取个人资料"""
    user = request.user
    # 先从缓存中获取数据
    profile_dict = cache.get(keys.PROFILE_DICT % user.id)
    # 如果能获取到就返回数据
    if profile_dict is not None:
        print('get profile from cache')
        return render_json(profile_dict)
    # 获取不到就从数据库中获取,并添加到缓存中.
    profile_dict = user.profile.to_dict()
    print('get profile dict from db')
    cache.set(keys.PROFILE_DICT % user.id, profile_dict, 86400 * 7)

    return render_json(profile_dict)


def edit_profile(request):
    """修改个人资料"""
    form = ProfileForm(request.POST)
    # user = User.get(id=request.session['uid'])
    if form.is_valid():
        profile = form.save(commit=False)
        profile.id = request.session['uid']
        profile.save()

        # 更新缓存
        cache.set(keys.PROFILE_DICT % profile.id, profile.to_dict(), 86400 * 7)
        # 记录日志
        logger.info(f'User {profile.id} has changed profile')
        return render_json(profile.to_dict())
    else:
        raise errors.ProfileErr(data=form.errors)


def upload_avatar(request):
    """头像上传"""
    avatar = request.FILES.get('avatar')
    # print(type(avatar))
    # print(avatar.name)
    uid = request.session['uid']
    user = User.get(id=uid)

    handle_upload_avatar.delay(user, avatar)

    return render_json(user.avatar)

#  想办法把耗时操作变成异步非阻塞的操作.
