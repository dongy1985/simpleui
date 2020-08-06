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
# 大分類:テンプレート分類
const.TEMPLATE_TYPE = '008'

# 小分類:開始時刻DEF
const.DEF_STARTTIME = '09:00'
# 小分類:終了時刻DEF
const.DEF_ENDTIME = '18:00'
# 小分類:休憩時間DEF
const.DEF_RESTTIME = '1.0'
# 小分類:実働時間DEF
const.DEF_WORKTIME = '8.0'
# 小分類:出勤区分DEF
const.DEF_DUTY = '0'
# 小分類:月度集計区分agg
const.AGG_MONTH = '1'
# 小分類:年度集計区分
const.AGG_YEAR = '2'
# 小分類:USERID_DEF
const.DEF_USERID = 0

# Excel管理
const.DIR = 'export/'
const.TEMPLATEPATH = 'export/template/勤務表model_v03.xlsm'
const.MONTH_TEMPLATEPATH = 'export/template/月度単位の集計表model.xlsx'
const.YEAR_TEMPLATEPATH = 'export/template/年度単位の集計表model.xlsx'
const.UNDERLINE = '_'
const.XLSX = '.xlsx'
const.XLSM = '.xlsm'
const.XLS = '.xlsx'
const.FILESTART = '/'
const.SHEET = '業務完了報告書Ver03'
const.SHEET_MONTH = '月度単位の集計表'
const.SHEET_YEAR = '年度単位の集計表'
# system email
const.ADMIN_MAIL = 'testid0917@gmail.com'
const.ADMIN_MAIL_PAS = 'testTest0917'
# メール区分
const.MAIL_KBN_COMMIT = '1'
const.MAIL_KBN_CANCEL = '2'
const.MAIL_KBN_CONFIRM = '3'
# 性别デフォルト
const.GENDER_DEF = '0'
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
const.TPL_XLS = '0'

# 資産管理用
# CharField 名前の長さ
const.NAME_LENGTH = 20

# CharField Textfield長文の長さ
const.TEXT_LENGTH = 128

# 申請借出状態default
const.LEND_STATUS = '0'

# 資産合計明細extra
const.EXTRA = 1

# 一ページ表示の数
const.PAGES = 8

# 資産状態 借出可否 可
const.LEND_OK = 1

# 資産状態 借出可否 否
const.LEND_NG = 0

# 資産借出申請 状態 申請提出済
const.LEND_REQUEST = '0'

# 資産借出申請 状態 申請承認済
const.LEND_APPLY = '1'

# 資産借出申請 状態 借出済
const.LEND_OUT = '2'

# 資産借出申請 状態 返却済
const.LEND_BACK = '3'

# 資産借出申請 状態 返却済
const.LEND_DENY = '4'

# 備考
const.DEF_COMMENT = ' '

# 一ページ表示の数
const.LIST_PER_PAGE = 30

# セル結合
const.SERU = ['C1:H1','I1:N1','O1:T1','U1:Z1',
              'AA1:AF1','AG1:AL1','Am1:AR1','AS1:AX1',
              'AY1:BD1','BE1:BJ1','BK1:BP1','BQ1:BV1',
              'BW1:CB1','CC1:CH1','CI1:CN1','CO1:CT1',
              'CU1:CZ1','DA1:DF1','DG1:DL1','DM1:DR1']
