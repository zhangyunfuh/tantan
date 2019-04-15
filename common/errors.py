"""各种自定义错误码"""


class LogicErr(Exception):
    code = None
    data = None

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.__class__.__name__


# 生成异常类工厂
def gen_logic_err(name, code):
    att_dict = {'code': code}
    return type(name, (LogicErr,), att_dict)


VcodeErr = gen_logic_err('VcodeErr', 1001)
ProfileErr = gen_logic_err('ProfileErr', 1002)
UserNotExist = gen_logic_err('UserNotExist', 1003)
LoginRequired = gen_logic_err('LoginRequired', 1004)
RewindLimit = gen_logic_err('RewindLimit', 1005)
PermissionErr = gen_logic_err('PermissionErr', 1006)
