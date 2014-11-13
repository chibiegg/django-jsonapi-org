# encoding=utf-8

from django.db import models

class Prefecture(models.Model):
    name = models.CharField("名称",max_length=5,unique=True)
    capital = models.CharField("県庁所在地", max_length=50)
    is_od = models.BooleanField("政令指定都市", default=False, blank=True)
    population = models.IntegerField("人口")

class Carrier(models.Model):
    name = models.CharField("名称", max_length=20, unique=True)

class User(models.Model):

    shimei = models.CharField("氏名", max_length=100)
    shimei_kana = models.CharField("氏名", max_length=100)
    email = models.EmailField("メールアドレス", blank=True)
    sex = models.CharField("性別", choices=(("M", "男性"), ("F", "女性")), max_length=1)
    birthdate = models.DateField("誕生日")
    is_married = models.BooleanField("婚姻", default=False, blank=True)
    blood_type = models.CharField("血液型", choices=(("A", "A"), ("B", "B"), ("O", "O"), ("AB", "AB")), max_length=2)
    prefecture = models.ForeignKey(Prefecture)
    tel = models.CharField("電話番号", max_length=12, blank=True)
    mobile = models.CharField("携帯番号", max_length=12, blank=True)
    carrier = models.ForeignKey(Carrier, blank=True, null=True)

