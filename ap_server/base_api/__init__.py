# -*- coding: UTF-8 -*-
# from base_api.api_blueprint import api, api_blueprint
from base_api.custom_cls import CustomMethodView, CustomRequestParser, CustomResource
from flask import Blueprint, Flask, request, session
from utils.mysql_utils import MysqlAccess

from .custom_cls import Api
#from apis.account.api import api as account_ns
from apis.account import auth, orders  # 匯入以觸發 route 註冊
from apis.account.model import api as account_ns

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_blueprint, version="0.0.1", description='', title='Kuohwa API Service', doc="/doc")


# init app
app = Flask(__name__, template_folder="../templates", static_folder="../static", static_url_path="")
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.secret_key = "test123456789"
app.config['JSON_AS_ASCII'] = False
# app.config['SESSION_CRYPTO_KEY'] = load_aes_key()
# app.config["SESSION_COOKIE_HTTPONLY"] = True
# app.session_interface = EncryptedSessionInterface()


# register blueprint
app.register_blueprint(api_blueprint)

# register swagger api
api.add_namespace(account_ns)

# # namespace
# account_api = api.namespace("account", description=u"帳號及權限管理")
# table_api = api.namespace("table", description=u"表格偵測結構")
# cell_api = api.namespace("cell", description=u"單元格類型標記")
# orc_api = api.namespace("orc", description=u"ORC文字辨識")
# history_api = api.namespace("history", description=u"歷史編輯紀錄")
