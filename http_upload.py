import datetime
import json
import requests

def http_put(self, data):
	# 获取apikey与apiurl
        	# 将“self.dictionaries['APIKEY']”和“self.dictionaries['apiurl']”自己上传设备的apikey和apiurl
        	# apikey = self.dictionaries['APIKEY']
        	# api_url = self.dictionaries['apiurl']
	apikey = '7HM214lMHeL3l1pCHIUkE0iPQvM='
	api_url = 'http://api.heclouds.com/devices/645647371/datapoints'
        	# data为要上传的数值
        	data_temperature = data
        	# 获取当前时间
        	curTime = datetime.datetime.now()
        	apiheaders = {'api-key': apikey, 'Content-Length': '120'}
        	# id为要上传的数据流名称，value为上传的值
        	payload_data_temperature = {'datastreams': [{"id": "aaa", "datapoints": [{"at": curTime.isoformat(), "value": data_temperature}]}]}
        	jdata_data_temperature = json.dumps(payload_data_temperature)  # 对数据进行JSON格式化编码
        	# 进行上传
        	requests.post(api_url, headers=apiheaders, data=jdata_data_temperature)

# 然后调用这个函数就行了
# data就是你要上传的数据
data = 12
while True:
	http_put(data)
