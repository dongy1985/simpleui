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
# 大分類:出勤区分
const.DUTY_TYPE = '001'
# 大分類:作業状態
const.WORK_TYPE = '002'
# 大分類:性別
const.GENDER_CD = '003'
# 大分類:社員状態(在職　離職)
const.EMPLOYEE_CD = '004'
# 大分類:Excel座標管理
const.CRD_DIV_CD = '005'
# 申請借出状態 大区分
const.BIG_STATUS = '006'
# 大分類:適用状態
const.DEL_STATUS_CD = '007'

# Excel管理
const.DIR = 'export/'
const.TEMPLATEPATH = 'export/template/勤務表model.xlsm'
const.UNDERLINE = '_'
const.XLSX = '.xlsm'
const.FILESTART = '/'
const.SHEET = '勤務表'
# system email
const.ADMIN_MAIL = 'testid0917@gmail.com'
const.ADMIN_MAIL_PAS = 'testTest0917'
# メール区分
const.MAIL_KBN_COMMIT = '1'
const.MAIL_KBN_CANCEL = '2'
const.MAIL_KBN_CONFIRM = '3'
# 性别デフォルト
const.GENDER_DEF = '1'
const.EMPLOYEE_DEF = '0'

# 作業状態小分類：0 未提出; 1 提出済; 2 承認済
const.WORK_TYPE_SMALL_0 = '0'
const.WORK_TYPE_SMALL_1 = '1'
const.WORK_TYPE_SMALL_2 = '2'


#   Excel座標管理
#   (0, 'ヘッダー部'),
#   (1, '明細部'),
#   (2, 'フッター部')

const.DEL_FLG_CD = '001'
const.DEL_FLG_0 = '0'
const.DEL_FLG_1 = '1'
const.DEF_DEL_FLG = '0'
const.CRD_DIV_H = '0'
const.CRD_DIV_D = '1'
const.CRD_DIV_F = '2'


# 資産管理用
# CharField 名前の長さ
const.NAME_LENGTH = 20

# CharField Textfield長文の長さ
const.TEXT_LENGTH = 128

# 申請借出状態default
const.LEND_STATUS = '001'

# 資産合計明細extra
const.EXTRA = 1

# 一ページ表示の数
const.PAGES = 8

# 資産状態 借出可否 可
const.LEND_OK = 1

# 資産状態 借出可否 否
const.LEND_NG = 0

# 資産借出申請 状態 申請提出済
const.LEND_REQUEST = '001'

# 資産借出申請 状態 申請承認済
const.LEND_APPLY = '002'

# 資産借出申請 状態 借出済
const.LEND_OUT = '003'

# 資産借出申請 状態 返却済
const.LEND_BACK = '004'

# 資産借出申請 状態 返却済
const.LEND_DENY = '005'