# Generated by Django 3.0.8 on 2020-08-04 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_crdmst'),
    ]

    operations = [
        migrations.AddField(
            model_name='crdmst',
            name='tplType',
            field=models.CharField(choices=[('0', '勤务EXCEL'), ('1', '月度単位の集計表'), ('2', '年度単位の集計表')], db_index=True, default='0', max_length=3, verbose_name='テンプレート分類'),
        ),
        migrations.AlterField(
            model_name='crdmst',
            name='crdDiv',
            field=models.CharField(choices=[('0', 'ヘッダ部'), ('1', '明細部'), ('2', 'フッター部')], db_index=True, default='0', max_length=3, verbose_name='座標分類'),
        ),
        migrations.AlterField(
            model_name='crdmst',
            name='crdX',
            field=models.IntegerField(help_text='数字で入力してください.', verbose_name='横座標'),
        ),
        migrations.AlterField(
            model_name='crdmst',
            name='crdY',
            field=models.IntegerField(help_text='数字で入力してください.', verbose_name='縦座標'),
        ),
        migrations.AlterField(
            model_name='crdmst',
            name='delFlg',
            field=models.CharField(choices=[('0', '有効'), ('1', '無効')], default='0', max_length=1, verbose_name='適用状態'),
        ),
        migrations.AlterField(
            model_name='crdmst',
            name='itemNm',
            field=models.CharField(help_text='20文字まで入力してください.', max_length=60, verbose_name='項目名'),
        ),
        migrations.AlterField(
            model_name='crdmst',
            name='itemSort',
            field=models.IntegerField(help_text='数字で３桁まで入力してください.', verbose_name='項目順'),
        ),
    ]
