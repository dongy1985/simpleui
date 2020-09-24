django simpleui demo.
---

<center>
<a href="https://github.com/newpanjing/simpleui">Simple UI源码</a> |
<a href="https://simpleui.88cto.com">Simple社区</a> 
</center>

simpleui demo,默认使用sqlite数据库。
启动步骤请查看下面的内容，如果你没有接触过django 或者 django admin，请先自己去django的官方查看相关文档学习。

simpleui 是一个django admin的ui框架，与代码无关。

# 自动安装
Linux或者macOS可以直接运行`bootstrap.sh`脚本，自动配置虚拟环境、安装依赖包、启动运行
```shell
sh ./bootstrap.sh
```

# 手动步骤

## 第一步
下载源码到本地
```shell
git clone https://github.com/newpanjing/simpleui_demo
```

## 第二步
安装依赖包

```shell
pip install -r requirements.txt
```

## 第三步
```shell
python manage.py runserver 192.168.22.103:8000 
```

## 第四步
打开浏览器，在地址栏输入以下网址
http://www2.jcbridge.co.jp:8000/

## 第五步
##  ユーザー　→ Password
①システム管理者：
    demo    → user.000
    simple  → user.000

②社長：
    test001 → user.001

③総務：
    test002 → user.002

④現場管理者：
    test003 → user.003
    test004 → user.004

⑤一般社員：
    test005 → user.005 → 「test003」と同じ現場
    test006 → user.006 → 「test004」と同じ現場
    test007 → user.007 → 「test004」と同じ現場
    test008 → user.008 → 「test004」と同じ現場