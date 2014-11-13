# encoding=utf-8
import jsonapi
from jsonapi.tests.dictdata import PrefectureData
from jsonapi.tests.forms import AddPrefectureForm, ChangePrefectureForm, \
    ModelAddPrefectureForm, ModelChangePrefectureForm
from jsonapi.models import ModelJSONAPI
from jsonapi.tests.models import Prefecture



class PrefectureJSONAPI(jsonapi.JSONAPI):
    model_name = "prefectures"
    add_form = AddPrefectureForm
    change_form = ChangePrefectureForm

    fields = (
              "id", "name", "capital", "is_od", "population",
              ("is_designated_by_ordinance", "is_od")
              )

    def get_items_for_request(self, request):
        return PrefectureData


prefectures = PrefectureJSONAPI()

class ModelPrefectureJSONAPI(ModelJSONAPI):
    model = Prefecture
    fields = (
              "id", "name", "capital", "is_od", "population",
              ("is_designated_by_ordinance", "is_od")
              )
    filters = (
               "name",
               ("population_gte", "population__gte"),
               )
    order_fields = ("population", ("od", "is_od"))
    add_form = ModelAddPrefectureForm
    change_form = ModelChangePrefectureForm

model_prefectures = ModelPrefectureJSONAPI()

