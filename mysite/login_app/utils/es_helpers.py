
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
                'permissions' : 'Low',
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

class UserControl():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('login_app/utils/config.ini')
        self.hosts = config['elasticsearch']['hosts']
        self.port = config['elasticsearch']['port']
        self.index = config['elasticsearch']['index']
        
        self.es = Elasticsearch(hosts=self.hosts, port=self.port)

    def time_format(self, timestamp_):
        date_time = datetime.fromtimestamp(timestamp_)
        time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")
        return time_str

    def user_list(self):
        query = {
            'query': {
                'match_all': {}
            }
        }
        ret = helpers.scan(self.es, index=self.index, query=query)
        data = []
        for i in ret:
            i['_source']['session_expire'] = self.time_format(
                i['_source']['session_expire'])
            i['_source']['created'] = self.time_format(i['_source']['created'])
            i['_source']['updated'] = self.time_format(i['_source']['updated'])
            data.append({
                'id': i['_id'],
                'source': i['_source']
            })
        return data

    def search_user_by_name(self, name):
        query = {
            'query': {
                'match': {
                    'name': name
                }
            }
        }
        ret = helpers.scan(self.es, index=self.index, query=query)
        ret = [i for i in ret]
        if len(ret) != 0:
            for i in ret:
                i['_source']['session_expire'] = self.time_format(
                    i['_source']['session_expire'])
                i['_source']['created'] = self.time_format(
                    i['_source']['created'])
                i['_source']['updated'] = self.time_format(
                    i['_source']['updated'])
            return ret
        else:
            ret = 0
            return ret

    def search_user_by_email(self, email):
        query = {
            'query': {
                'match': {
                    'email': email
                }
            }
        }
        ret = self.es.search(index=self.index, body=query)
        if len(ret['hits']['hits']) != 0:
            ret = ret['hits']['hits'][0]
            ret['_source']['session_expire'] = self.time_format(
                ret['_source']['session_expire'])
            ret['_source']['created'] = self.time_format(
                ret['_source']['created'])
            ret['_source']['updated'] = self.time_format(
                ret['_source']['updated'])

            return ret
        else:
            ret = 0
            return ret

    def search_user_by_id(self, id_list):
        query = {
            'query': {
                'bool': {
                    'must': {
                        'terms': {'_id': id_list}
                    }
                }
            }
        }
        ret = helpers.scan(self.es, index=self.index, query=query)
        data = []
        for i in ret:
            i['_source']['session_expire'] = self.time_format(
                i['_source']['session_expire'])
            data.append({'id': i['_id'], 'source': i['_source']})
        return data

    def update(self, up_list):
        try:
            user = []
            for i in up_list:
                body = {
                    'query': {
                        'match': {'email': i['email']}
                    }
                }
                ret = self.es.search(index=self.index, body=body)
                if len(ret['hits']['hits']) != 0:
                    session_ex = ret['hits']['hits'][0]['_source']['session_expire']
                    _id = ret['hits']['hits'][0]['_id']
                    date_time = datetime.fromtimestamp(session_ex)
                    expir = timedelta(days=i['session_expire'])
                    ex = date_time + expir
                    ex = ex.timestamp()
                    d = {
                        '_op_type': 'update',
                        '_index': self.index,
                        '_id': _id,
                        'doc': {
                            'name': i['name'],
                            'session_expire': int(ex),
                            'permissions': i['permissions'],
                            'updated': int(datetime.now().timestamp())
                        }
                    }
                    user.append(d)
            #     self.es.update(index=self.index, body={'doc':d}, id=_id)
            helpers.bulk(self.es, user)
            ret = {'status': 'success'}
        except:
            ret = {'status': 'error'}
        return ret

    def delete_user(self, id_list):
        delete = []
        for i in id_list:
            delete.append({
                '_op_type': 'delete',
                '_index': self.index,
                '_id': i
            })
        try:
            helpers.bulk(self.es, delete)
            ret = 'success'
        except Exception as e:
            ret = 'error'
        return ret