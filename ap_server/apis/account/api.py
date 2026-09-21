from apis.account.model import *
from apis.account.module import *
from flask import session
from base_api import CustomResource
from flask import request
import os
from werkzeug.utils import secure_filename


ROLE_ADMIN = "Admin"


@api.route("/test")
class Login2(CustomResource):
    allow_roles = [ROLE_ADMIN]
    def post(self):
        print(api.payload)
        return "OK"


@api.route("/login")
class Login(CustomResource):
    @api.expect(account_input_payload)
    @api.marshal_with(account_output_payload)
    def post(self):
        data = api.payload
        result = Account.login(username=data["username"], passwd=data["passwd"])
        if result.get("result") == 0:
            session["roles"] = [ROLE_ADMIN]
        return result


@api.route("/forget")
class Forget(CustomResource):
    @api.expect(forget_input_payload)
    def post(self):
        data=api.payload
        return Account.forget(user_id=data["user_id"])


@api.route("/get_account_list")
class get_account_list(CustomResource):
    allow_roles = [ROLE_ADMIN]
    def get(self):
        return Account.get_account_list()


@api.route("/add_account_list")
class add_account_list(CustomResource):
    allow_roles = [ROLE_ADMIN]
    @api.expect(addaccount_input_payload)
    def post(self):
        data=api.payload
        session["roles"] = [ROLE_ADMIN]
        return Account.add_account_list(user_id=data["user_id"], role=data["role"], email=data["email"])

@api.route("/delete_account_list")
class delete_account_list(CustomResource):
    allow_roles = [ROLE_ADMIN]
    @api.expect(delete_account_payload)
    def post(self):
        data=api.payload
        session["roles"] = [ROLE_ADMIN]
        return Account.delete_account_list(user_id=data["user_id"])

@api.route("/update_account_list")
class update_account_list(CustomResource):
    allow_roles = [ROLE_ADMIN]
    
    @api.expect(update_account_payload)
    def post(self):
        data = api.payload
        session["roles"] = [ROLE_ADMIN]
        return Account.update_account_list(
            old_user_id=data["old_user_id"],
            data=data["data"]
        )

@api.route("/autosave_detect_table")
class autosave_detect_table(CustomResource):
    allow_roles=[ROLE_ADMIN]
    @api.expect(autosave_detect_table_payload)
    def post(self):
        data=api.payload
        session["roles"] = [ROLE_ADMIN]
        return Account.autosave_detect_table(
            uuid=data["uuid"],
            data=data["data"]
        )

@api.route("/get_detect_table")
class get_detect_table(CustomResource):
    allow_roles=[ROLE_ADMIN]
    @api.expect(get_detect_table_payload)
    def post(self):
        data=api.payload
        session["roles"] = [ROLE_ADMIN]
        return Account.get_detect_table(data["uuid"])