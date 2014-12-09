# encoding=utf-8

import json
from django.test import TestCase


class JSONAPIFormTest(TestCase):

    def setUp(self):
        from jsonapi import forms
        class BooleanForm(forms.Form):
            f = forms.BooleanField(label="Bool", required=False)
        class RequiredBooleanForm(forms.Form):
            f = forms.BooleanField(label="Bool", required=True)

        self.form_class = BooleanForm
        self.required_form_class = RequiredBooleanForm

    def test_false(self):
        data = {"f":False}
        f = self.form_class(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data, data)

    def test_true(self):
        data = {"f":True}
        f = self.form_class(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data, data)

    def test_required_false(self):
        data = {"f":False}
        f = self.required_form_class(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data, data)

    def test_required_true(self):
        data = {"f":True}
        f = self.required_form_class(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data, data)

    def test_not_required(self):
        data = {}
        f = self.form_class(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data, {"f":None})

    def test_required(self):
        data = {}
        f = self.required_form_class(data)
        self.assertFalse(f.is_valid())



