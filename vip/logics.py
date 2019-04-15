from common import errors


def need_perm(perm_name):
    def deco(view_func):
        def wrap(request, *args, **kwargs):
            # 如果用户有某个权限的话.就正常执行视图函数
            user = request.user
            print('会员信息', user.vip)
            print(user.vip.perms)
            if user.vip.has_perm(perm_name):
                response = view_func(request, *args, **kwargs)
                return response
            else:
                # 如果没有的话, raise 一个没有权限的错误.
                raise errors.PermissionErr('权限不足, 请提示vip等级')
        return wrap
    return deco
