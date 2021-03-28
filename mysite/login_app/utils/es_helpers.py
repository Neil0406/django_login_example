
from elasticsearch import Elasticsearch, helpers
from datetime import datetime, timedelta
import configparser


class User():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('login_app/utils/config.ini')
        self.hosts = config['elasticsearch']['hosts']
        self.port = config['elasticsearch']['port']
        self.index = config['elasticsearch']['index']
        
        self.es = Elasticsearch(hosts=self.hosts, port=self.port)

    def create_user(self, name, email, password_key, password_value):
        body = {
            'query':{
                'match':{
                    'email':email
                }
            }
        }
        ret = self.es.count(index=self.index, body=body)
        if ret['count'] == 0:
            now = datetime.now()
            expir= timedelta(days = 7)
            ex = now + expir
            ex = ex.timestamp()
            create = {
                'name':name, 
                'email':email, 
                'password_key':password_key, 
                'password_value':password_value,
                'session_expire': int(ex),
                'created': int(datetime.now().timestamp()),
                'updated': int(datetime.now().timestamp())
            }
            self.es.index(index=self.index, body=create)
            ret = 'success'
        else:
            ret = 'exists'
        return ret

    def set_session_expire(self, _id):
        '''
        # 新建立使用者寫入 session 有效時間 
        # 登入使用者寫入 session 有效時間
        '''
        now = datetime.now()
        expir= timedelta(days = 7)
        ex = now + expir
        ex = ex.timestamp()
        self.es.update(index=self.index, body={'doc':{'session_expire':int(ex)}}, id=_id)

    def get_user_info(self, email):
        '''
        # 檢查 session 時間 
        # 取得 user 資料 
        '''
        now = datetime.now()
        body = {
            'query':{
                'bool':{
                    'must':{
                        'match':{
                            'email':email
                        }
                    },
                    'filter':{
                        'range':{
                            'session_expire':{'gte':int(now.timestamp())}
                        }
                    }
                }
            }
        }
        ret = self.es.search(index=self.index, body=body)
        if len(ret['hits']['hits']) == 0:
            user = 0
        else:
            user = ret['hits']['hits'][0]
        return user

    def check_login(self, email):
        body = {
            'query':{
                'match':{
                    'email':email
                }
            }
        }
        ret = self.es.search(index=self.index, body=body)
        if len(ret['hits']['hits']) == 0:
            user = 0
        else:
            user = ret['hits']['hits'][0]
        return user


