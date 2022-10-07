import os
import ProxyCloud

#Bot Config
BOT_TOKEN = os.environ.get('bot_token','5416621607:AAEMRkILmaBRguP697w-QjCZEywp_hBNVVI')
#Storage Config
BASE_ROOT_PATH = 'root/'
#Account Config
OWN_USER = os.environ.get('account_user','ljgaliano')
OWN_PASSWORD = os.environ.get('account_password','Pelusa1234//')
# Proxy Config
PROXY_OBJ = ProxyCloud.parse(os.environ.get('proxy_enc',))
# Sync Options
SPLIT_SYNC = 1024 * 1024 * int(os.environ.get('split_sync',10))
UPLOAD_SYNC = 3