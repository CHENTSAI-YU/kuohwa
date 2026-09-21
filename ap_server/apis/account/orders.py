from apis.account.model import *
from apis.account.module import *
from flask import session
from base_api import CustomResource

ROLE_ADMIN = "Admin"

#6
@api.route("/autosave_detect_table")
class AutosaveDetectTable(CustomResource):
    @api.expect(autosave_detect_table_payload)
    @api.marshal_with(output_payload)
    def post(self):
        data = api.payload
        result= Account.autosave_detect_table(
            uuid=data["uuid"],
            data=data["data"]
        )

        if result.get("result")!=0:
            return result, 400

        return result, 200


#7
@api.route("/get_detect_table")
class GetDetectTable(CustomResource):
    @api.expect(get_detect_table_payload)
    @api.marshal_with(getdetecttable_output_payload)
    def post(self):
        data=api.payload
        result=Account.get_detect_table(uuid=data["uuid"])
        if result.get("result")!=0:
            return result, 400

        return result, 200
#8
@api.route("/get_key_value_mapping")
class GetKeyValueMapping(CustomResource):
    @api.expect(get_key_value_mapping_payload)
    @api.marshal_with(getkeyvalue_output_payload)
    def post(self):
        data=api.payload
        result= Account.get_key_value_mapping(vendor=data["vendor"],file_type= data["file_type"])

        if result.get("result")!=0:
            return result, 400

        return result, 200
#9
@api.route("/autosave_key_value_mapping")
class AutosaveKeyValueMapping(CustomResource):
    @api.expect(autosave_key_value_mapping_payload)
    @api.marshal_with(output_payload)
    def post(self):
        payload = api.payload #payload 是字典
        data = payload.get("data", [])  # 去拿 Key 為 "data" 的內容
        result=Account.autosave_key_value_mapping(data)

        if result.get("result")!=0:
            return result, 400

        return result, 200
#10
@api.route("/get_image_path")
class GetImagePath(CustomResource):
    @api.expect(get_image_path_payload)
    @api.marshal_with(getimage_output_payload)
    def post(self):
        data=api.payload
        result=Account.get_image_path(uuid=data["uuid"])
        if result.get("result")!=0:
            return result, 400

        return result, 200
#11
@api.route("/autosave_image_path")
class autosave_image_path(CustomResource):
    @api.expect(autosave_image_path_payload)
    @api.marshal_with(output_payload)
    def post(self):
        data=api.payload
        result= Account.autosave_image_path(uuid=data["uuid"], front_path=data["front_path"], back_path=data["back_path"])
        if result.get("result")!=0:
            return result, 400

        return result, 200