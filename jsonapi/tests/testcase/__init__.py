# encoding=utf-8

import datetime
import json
from django.test import TestCase
from django.test.client import Client

class JST(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=9)
    def dst(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return 'JST'


class JSONAPITest(TestCase):

    def setUp(self):
        from jsonapi.tests.views import PrefectureJSONAPI
        self.api = PrefectureJSONAPI()
        self.client = Client()

    def test_date(self):
        d = datetime.date(2014, 10, 12)
        self.assertEqual(self.api.json_serialize(d), "2014-10-12", "Invalid serialize of `datetime.date` type.")

    def test_datetime(self):
        dt = datetime.datetime(2014, 9, 20, 15, 2, 4)
        self.assertEqual(self.api.json_serialize(dt), "2014-09-20T15:02:04", "Invalid serialize of `datetime.date` type.")

    def test_datetime_tz(self):
        dt = datetime.datetime(2014, 9, 20, 15, 2, 4).replace(tzinfo=JST())
        self.assertEqual(self.api.json_serialize(dt), "2014-09-20T15:02:04+09:00", "Invalid serialize of `datetime.date` type.")


    def test_get_index(self):
        response = self.client.get("/prefectures/")
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("prefectures" in response)
        prefectures = response["prefectures"]
        original_prefectures = self.api.get_items_for_request(None)
        self.assertTrue(isinstance(prefectures, list))
        self.assertEqual(len(prefectures), 47)
        for i, pref in enumerate(prefectures):
            # Asseret Equal to OriginalData
            for field in ("id", "name", "capital", "is_od", "population"):
                self.assertEqual(pref[field], original_prefectures[i][field])

            # Change Attribute Name
            self.assertEqual(pref["is_designated_by_ordinance"], pref["is_od"])

    def test_get_item(self):
        """単一Itemの取得"""
        id = 27
        response = self.client.get("/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("prefectures" in response)
        prefecture = response["prefectures"]
        original_prefecture = self.api.get_items_for_request(None)[id - 1]
        self.assertTrue(isinstance(prefecture, dict))

        for field in ("id", "name", "is_od", "capital", "population"):
            self.assertEqual(prefecture[field], original_prefecture[field])


    def test_get_item_notfound(self):
        """存在しないIDのため 404 NotFound"""
        id = 100
        response = self.client.get("/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 404, "Status Code is not 404")


    def test_delete_item(self):
        """202 Accepted"""
        id = 27
        response = self.client.delete("/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 202, "Status Code is not 202")


    def test_delete_item_invalid_id(self):
        """IDが存在しないため 404 NotFound"""
        id = 100
        response = self.client.delete("/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 404, "Status Code is not 404")

    def test_put_index(self):
        """対応しないリクエスト"""
        response = self.client.put("/prefectures/")
        self.assertEqual(response.status_code, 405, "Status Code is not 405")

    def test_post_index_wo_form(self):
        """AddFormがないため 405 NotAllowed"""
        from jsonapi.tests.views import prefectures as prefectures_api
        prefectures_api.add_form = None
        request = {
                   "prefectures" : {
                                    "name":"架空県"
                                    }
                   }
        response = self.client.post("/prefectures/", data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 405, "Status Code is not 405")


    def test_post_index_single(self):
        """Item追加"""
        pref_data_1 = {
                     "name":"架空1県",
                     "capital":"架空1市",
                     "is_od":True,
                     "population":100
                    }
        request = {
                   "prefectures" :pref_data_1
                   }
        response = self.client.post("/prefectures/", data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("prefectures" in response)
        self.assertTrue(isinstance(response["prefectures"], list))
        self.assertEqual(len(response["prefectures"]), 1)

        pref_data_1["id"] = 48
        pref_data_1["is_designated_by_ordinance"] = True
        self.assertEqual(response["prefectures"][0], pref_data_1)



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
                     "is_od":False,
                     "population":200
                    }
        request = {
                   "prefectures" : [pref_data_1, pref_data_2]
                   }
        response = self.client.post("/prefectures/", data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("prefectures" in response)
        self.assertTrue(isinstance(response["prefectures"], list))
        self.assertEqual(len(response["prefectures"]), 2)

        pref_data_1["id"] = 48
        pref_data_1["is_designated_by_ordinance"] = True
        self.assertEqual(response["prefectures"][0], pref_data_1)

        pref_data_2["id"] = 48
        pref_data_2["is_designated_by_ordinance"] = False
        self.assertEqual(response["prefectures"][1], pref_data_2)


    def test_post_index_invalid_struct(self):
        """構造誤りのため 400 BadRequest"""
        request = {
                   "pref" : {}
                   }
        response = self.client.post("/prefectures/", data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 400, "Status Code is not 400")


    def test_post_index_invalid_data(self):
        """データ誤りのため 400 BadRequest"""

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
                     "population":"deafbeaf"
                    }
        request = {
                   "prefectures" : [pref_data_1, pref_data_2]
                   }
        response = self.client.post("/prefectures/", data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 400, "Status Code is not 400")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue(isinstance(response, list))
        self.assertTrue(len(response), 2)
        self.assertEqual(response[0], {})
        self.assertTrue("population" in response[1])

    def test_post_item(self):
        """対応しないリクエストのため 405 NotAllowed"""
        response = self.client.post("/prefectures/{0}/".format(id))
        self.assertEqual(response.status_code, 405, "Status Code is not 405")

    def test_put_item_wo_form(self):
        """ChangeFormがないため 405 NotAllowed"""
        from jsonapi.tests.views import prefectures as prefectures_api
        prefectures_api.change_form = None
        id = 27
        request = {
                   "prefectures" : {
                                    "id":id,
                                    "name":"架空県"
                                    }
                   }
        response = self.client.put("/prefectures/{0}/".format(id), data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 405, "Status Code is not 405")



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
        response = self.client.put("/prefectures/{0}/".format(id), data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        pref_data["is_designated_by_ordinance"] = pref_data["is_od"]
        self.assertEqual(response["prefectures"], pref_data)




    def test_put_item_invalid_struct(self):
        """存在しないIDのため 400 NotFound"""
        id = 27
        pref_data = {
                     "id":id,
                     "name":"架空県",
                     "capital":"架空市",
                     "is_od":True,
                     "population":1000
                    }
        request = {
                   "pref":pref_data
                   }
        response = self.client.put("/prefectures/{0}/".format(id), data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 400, "Status Code is not 400")



    def test_put_item_invalid_id(self):
        """存在しないIDのため 400 NotFound"""
        id = 100
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
        response = self.client.put("/prefectures/{0}/".format(id), data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 404, "Status Code is not 404")


    def test_put_item_invalid_data(self):
        """誤ったデータのため 400 NotFound"""
        id = 27
        pref_data = {
                     "id":id,
                     "name":"架空県",
                     "capital":"架空市",
                     "is_od":True,
                     "population":"deadbeaf"
                    }
        request = {
                   "prefectures":pref_data
                   }
        response = self.client.put("/prefectures/{0}/".format(id), data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 400, "Status Code is not 400")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("population" in response)


    def test_metadata(self):
        """metadataの追加"""
        metadata = {"hoge":"fuga"}
        from jsonapi.tests.views import prefectures as prefectures_api
        prefectures_api.metadata = metadata


        response = self.client.get("/prefectures/")
        self.assertEqual(response.status_code, 200, "Status Code is not 200")
        response = json.loads(response.content.decode("utf-8"))

        self.assertTrue("meta" in response)
        self.assertEqual(response["meta"], metadata)


