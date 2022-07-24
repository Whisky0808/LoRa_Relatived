import requests
import os

# master-apikey = 'x2YoKTwtI7TCOvCyRu=Xt5gLBhU='
# 添加、删除设备使用产品的master-apikey
# url = 'http://api.heclouds.com/devices'
if __name__ == '__main__':
	url = 'http://api.heclouds.com/devices'
	headers = {'api-key':"x2YoKTwtI7TCOvCyRu=Xt5gLBhU="}
	params = {'title': "test_device"}

	response = requests.request("POST", url, headers=headers, json=params)
	print(response.text)
	os.system("pause")