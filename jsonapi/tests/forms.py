# encoding=utf-8

from django import forms
from jsonapi.tests.dictdata import PrefectureData
from jsonapi.tests.models import Prefecture

class AddPrefectureForm(forms.Form):
    
    id = forms.IntegerField(label="ID", required=False)
    name = forms.CharField(label="名称",required=True)
    capital = forms.CharField(label="県庁所在地", required=True)
    is_od = forms.BooleanField(label="政令指定都市かどうか", required=False)
    population = forms.IntegerField(label="人口", required=True)


    def clean_id(self):
        value = self.cleaned_data['id']
        if value:
            raise forms.ValidationError("Cannot Set ID")
        return value

    def clean(self):
        cleaned_data = super(AddPrefectureForm, self).clean()
        if cleaned_data["id"] is None:
            cleaned_data["id"] = PrefectureData[-1]["id"] + 1
        return cleaned_data



class ChangePrefectureForm(AddPrefectureForm):


    def clean_id(self):
        value = self.cleaned_data['id']
        if value != self.initial["id"]:
            raise forms.ValidationError("Cannot Change ID")
        return value


class ModelAddPrefectureForm(forms.ModelForm):
    id = forms.IntegerField(label="ID", required=False)

    class Meta:
        model = Prefecture
        fields = ("name", "capital", "is_od", "population")

    def clean_id(self):
        value = self.cleaned_data['id']
        if value:
            raise forms.ValidationError("Cannot Set ID")
        return value


class ModelChangePrefectureForm(forms.ModelForm):
    id = forms.IntegerField(label="ID", required=False)

    class Meta:
        model = Prefecture
        fields = ("capital", "population")

    def clean_id(self):
        value = self.cleaned_data['id']
        if value != self.instance.id:
            raise forms.ValidationError("Cannot Change ID")
        return value

