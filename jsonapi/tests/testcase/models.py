# encoding=utf-8

import datetime
import json
from django.test import TestCase
from django.test.client import Client
from jsonapi.tests.models import Prefecture
from jsonapi.tests.testcase import JST

class ModelJSONAPITest(TestCase):
    fixtures = ['prefecture.json', 'carrier.json', 'user.json']

    def setUp(self):
        from jsonapi.tests.views import model_prefectures
        self.prefecture_api = model_prefectures
        self.client = Client()

    def test_json_serialize(self):
        """モデルのシリアライズは`id`を用いる"""
        id = 27
        pref = Prefecture.objects.get(id=id)
        self.assertEqual(self.prefecture_api.json_serialize(pref), id)

    def test_date(self):
        d = datetime.date(2014, 10, 12)
        self.assertEqual(self.prefecture_api.json_serialize(d), "2014-10-12", "Invalid serialize of `datetime.date` type.")

    def test_datetime(self):
        dt = datetime.datetime(2014, 9, 20, 15, 2, 4)
        self.assertEqual(self.prefecture_api.json_serialize(dt), "2014-09-20T15:02:04", "Invalid serialize of `datetime.date` type.")

    def test_datetime_tz(self):
        dt = datetime.datetime(2014, 9, 20, 15, 2, 4).replace(tzinfo=JST())
        self.assertEqual(self.prefecture_api.json_serialize(dt), "2014-09-20T15:02:04+09:00", "Invalid serialize of `datetime.date` type.")

    def test_debug_query_false(self):
        """クエリデバッグ情報なし"""
        from django.conf import settings
        settings.DEBUG = False
        response = self.client.get("/models/prefectures/")
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode("utf-8"))

        self.assertFalse("queries" in response.get("meta", {}))

    def test_debug_query_true(self):
        """クエリデバッグ情報あり"""
        from django.conf import settings
        settings.DEBUG = True
        response = self.client.get("/models/prefectures/")
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("meta" in response)
        self.assertTrue("queries" in response["meta"])

    def test_get_queryset(self):
        """全件取得"""
        self.assertEqual(self.prefecture_api.get_queryset(None).count(), 47)

    def test_get_item_by_id(self):
        """ID指定取得"""
        id = 27
        pref = self.prefecture_api.get_item_by_id(None, id)
        self.assertEqual(pref.id, 27)

    def test_get_index(self):
        response = self.client.get("/models/prefectures/")
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("prefectures" in response)
        self.assertEqual(len(response["prefectures"]), 47)

    def test_get_item(self):
        id = 27
        response = self.client.get("/models/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("prefectures" in response)
        self.assertEqual(response["prefectures"]["id"], id)


    def test_delete_item(self):
        """削除はAccepted"""
        id = 27
        response = self.client.delete("/models/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 202)

        # 削除されたことを確認する
        self.assertFalse(Prefecture.objects.filter(id=id).exists())

    def test_delete_invalid_id(self):
        """存在しないIDのため 404 NotFound"""
        id = 100
        response = self.client.delete("/models/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 404)

    def test_post_index(self):
        """Item追加"""
        pref_data_1 = {
                     "name":"架空1県",
                     "capital":"架空1市",
                     "is_od":True,
                     "population":100
                    }
        pref_data_2 = {
                     "name":"架空2県",
                     "capital":"架空2市",
                     "is_od":True,
                     "population":200
                    }
        request = {
                   "prefectures" : [pref_data_1, pref_data_2]
                   }
        response = self.client.post("/models/prefectures/", data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("prefectures" in response)
        self.assertTrue(isinstance(response["prefectures"], list))
        self.assertEqual(len(response["prefectures"]), 2)

        pref_data_1["id"] = 48
        pref_data_1["is_designated_by_ordinance"] = True
        self.assertEqual(response["prefectures"][0], pref_data_1)
        self.assertTrue(Prefecture.objects.filter(id=48).exists())


        pref_data_2["id"] = 49
        pref_data_2["is_designated_by_ordinance"] = True
        self.assertEqual(response["prefectures"][1], pref_data_2)
        self.assertTrue(Prefecture.objects.filter(id=49).exists())


    def test_put_item(self):
        """Itemの変更"""
        id = 27
        pref_data = {
                     "id":id,
                     "name":"架空県",
                     "capital":"架空市",
                     "is_od":True,
                     "population":100
                    }
        request = {
                   "prefectures":pref_data
                   }
        response = self.client.put("/models/prefectures/{0}/".format(id), data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        pref_data["name"] = "大阪府"  # 変更不可
        pref_data["is_designated_by_ordinance"] = pref_data["is_od"]
        self.assertEqual(response["prefectures"], pref_data)


    def test_filter(self):
        """単純な一致判定"""
        response = self.client.get("/models/prefectures/", {"name":"大阪府"})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), 1)
        self.assertEqual(response["prefectures"][0]["id"], 27)

    def test_filter_rename(self):
        """フィールド名とフィルタ名のことなる検索"""
        population_gte = 8856000  # 大阪府の人口

        response = self.client.get("/models/prefectures/", {"population_gte": population_gte})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), 3)


    def test_order_asc(self):
        """昇順ソート"""
        response = self.client.get("/models/prefectures/", {"sort": "population"})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), 47)
        before_population = 0

        for pref in response["prefectures"]:
            self.assertTrue(before_population <= pref["population"])
            before_population = pref["population"]


    def test_order_desc(self):
        """降順ソート"""
        response = self.client.get("/models/prefectures/", {"sort": "-population"})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), 47)
        before_population = 100000000000

        for pref in response["prefectures"]:
            self.assertTrue(before_population >= pref["population"])
            before_population = pref["population"]

    def test_order_rename_asc(self):
        """昇順ソート"""
        response = self.client.get("/models/prefectures/", {"sort": "od"})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), 47)
        before_od = False

        for pref in response["prefectures"]:
            self.assertTrue(before_od <= pref["is_od"])
            before_od = pref["is_od"]

    def test_pagenation(self):
        per_page = 5
        response = self.client.get("/models/prefectures/", {"per_page": per_page})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), per_page)

        self.assertEqual(response["prefectures"][0]["id"], 1)
        self.assertEqual(response["meta"]["total"], 47)
        self.assertEqual(response["meta"]["per_page"], per_page)
        self.assertEqual(response["meta"]["page"], 1)

    def test_pagenation_middle_page(self):
        per_page = 5
        page = 3
        response = self.client.get("/models/prefectures/", {"per_page": per_page, "page":page})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), per_page)

        self.assertEqual(response["prefectures"][0]["id"], 11)
        self.assertEqual(response["meta"]["total"], 47)
        self.assertEqual(response["meta"]["per_page"], per_page)
        self.assertEqual(response["meta"]["page"], page)

    def test_pagenation_invalid_page(self):
        per_page = 5
        page = "deadbeaf"
        response = self.client.get("/models/prefectures/", {"per_page": per_page, "page":page})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), per_page)

        self.assertEqual(response["meta"]["total"], 47)
        self.assertEqual(response["meta"]["per_page"], per_page)
        self.assertEqual(response["meta"]["page"], 1)

    def test_pagenation_over_page(self):
        per_page = 5
        page = 1000
        response = self.client.get("/models/prefectures/", {"per_page": per_page, "page":page})
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(response["prefectures"]), per_page)

        self.assertEqual(response["meta"]["total"], 47)
        self.assertEqual(response["meta"]["per_page"], per_page)
        self.assertEqual(response["meta"]["page"], 1)



