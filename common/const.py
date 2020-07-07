import sys

class _const:
    class ConstError(PermissionError):
        pass
    class ConstCaseError(ConstError):
        pass
    def __setattr__(self, name, value):
        if name in self.__dict__: 
            raise self.ConstError("Can't change const {0}".format(name))
        if not name.isupper(): 
            raise self.ConstCaseError("const name {0} is not all uppercase".format(name))
        self.__dict__[name] = value

const = _const()
const.DUTY_TYPE = '003'
const.EXCEL_COORDINATE = "005"
const.DIR = 'export/'
const.TEMPLATEPATH = 'export/template/勤務表model.xlsx'
const.UNDERLINE = '_'
const.XLSX = '.xlsx'
const.FILESTART = '/'
const.SHEET = '勤務表'
const.HEAD = '01'
const.DATA = '02'
const.ADMIN_ID = 1
const.ADMIN_MAIL = 'testid0917@gmail.com'
const.ADMIN_MAIL_PAS = 'testTest0917'
const.MAIL_KBN_COMMIT = 1
const.MAIL_KBN_CANCEL = 2
const.MAIL_KBN_CONFIRM = 3
const.GENDER_DEF = '1'
const.EMPLOYEE_DEF = '1'
const.GENDER_CD = '4'
const.EMPLOYEE_CD = '5'
# 作業状態区分004　未提出、提出済、承認済
const.WORK_TYPE = '004'


#   Excel座標管理
#   (0, 'ヘッダー部'),
#   (1, '明細部'),
#   (2, 'フッター部')

const.DEL_FLG_CD = '001'
const.DEL_FLG_0 = '0'
const.DEL_FLG_1 = '1'
const.DEF_DEL_FLG = '0'
const.CRD_DIV_H = '0'
const.CRD_DIV_CD = '006'
