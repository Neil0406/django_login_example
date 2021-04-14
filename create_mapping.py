from datetime import datetime
from elasticsearch import helpers, Elasticsearch
from mysite.login_app.utils.password_encode import PasswordEncode


class CreateIndex():
    def create_index(self, es):
        body = dict()
        body['settings'] = self.get_setting()
        body['mappings'] = self.get_mappings()
        es.indices.create(index='a_user_info', body=body)

    def get_setting(self):
        settings = {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        }
        return settings

    def get_mappings(self):
        mappings = {
            "dynamic": "strict",
            "properties": {
                "name": {
                    "type": "text"
                },
                'email':{
                    "type": "keyword"
                },
                "password_key":{
                    "type": "keyword"
                },
                "password_value":{
                    "type": "keyword"
                },
                'session_expire':{
                    "type": "date",
                    "format": "epoch_second"
                },
                'permissions':{
                    "type": "keyword"
                },
                'picture':{
                    "type": "keyword",
                    'index': 'false'
                },
                "created": {
                        "type": "date",
                        "format": "epoch_second"
                },
                "updated": {
                    "type": "date",
                    "format": "epoch_second"
                }
            }
        }
        return mappings

if __name__ == "__main__":
    es = Elasticsearch(hosts='localhost', port=9200)
    CreateIndex().create_index(es)
    es.indices.put_alias(index='a_user_info', name='user_info')

    name = input('Your Name :')
    email = input('Your Email :')
    password = input('Your password :')
    PasswordEncode = PasswordEncode()
    key, encryptstr = PasswordEncode.encrypt(password)
    datetime = datetime.now().timestamp()

    body = {
        'name':name, 
        'email':email, 
        'password_key': key,
        'password_value': encryptstr,
        'permissions' : 'Height',
        'updated': int(datetime),
        'created': int(datetime)
    }
    ret = es.index(index='a_user_info', body=body)
    print(ret)
