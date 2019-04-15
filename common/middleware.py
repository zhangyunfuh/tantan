from django.utils.deprecation import MiddlewareMixin

from user.models import User
from lib.http import render_json
from common import errors
from common import errors


class AuthMidddleware(MiddlewareMixin):
    # 请求的路径白名单
    URL_WHITE_LIST = [
        '/api/user/submit/phone/',
        '/api/user/submit/vcode/'
    ]

    def process_request(self, request):
        if request.path in self.URL_WHITE_LIST:
            return
        uid = request.session.get('uid')
        if uid:
            try:
                user = User.get(id=uid)
                request.user = user
                return
            except User.DoesNotExist:
                return render_json('用户不存在', errors.UserNotExist.code)

        else:
            return render_json('请登录', errors.LoginRequired.code)


# process_excetption # 会捕获视图函数的错误.

class LogicErrMiddleware(MiddlewareMixin):
    # 中间件中的process_exception只会捕获视图函数的错误.
    def process_exception(self, request, exception):
        # 判断exception是不是我们定义的异常.
        # print('excepting....')
        # print(exception)
        # print(type(exception))
        if isinstance(exception, errors.LogicErr):
            print(exception)
            return render_json(exception.data, exception.code)


