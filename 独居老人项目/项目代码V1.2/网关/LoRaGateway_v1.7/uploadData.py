import equipmentMessage
import datetime
import json
import requests


class UploadData:
    """获得设备的APIKEY和apiurl,以及上传数据"""
    def __init__(self):
        pass

    def getAPI(self, information):
        self.dictionaries = equipmentMessage.get_API_Information(information)
        
    def http_put(self, information):
        # data_kind = self.dictionaries['datakind']
        # 获取apikey与apiurl
        apikey = self.dictionaries['APIKEY']
        api_url = self.dictionaries['apiurl']
        # 获取要上传的数值
        data_temperature = float(information['temperature'])
        data_Humidity = float(information['Humidity'])
        data_Pressure = float(information['Pressure'])
        isFall = information['isFall']
        isCure = information['isCure']
        # 获取当前时间
        curTime = datetime.datetime.now()
        apiheaders = {'api-key': apikey, 'Content-Length': '120'}
        # id为要上传的数据流名称，value为上传的值
        payload_data_temperature = {
            'datastreams': [{"id": "temperature", "datapoints": [{"at": curTime.isoformat(), "value": data_temperature}]}]}
        payload_data_Humidity = {
            'datastreams': [{"id": "Humidity", "datapoints": [{"at": curTime.isoformat(), "value": data_Humidity}]}]}
        payload_data_Pressure = {
            'datastreams': [{"id": "Pressure", "datapoints": [{"at": curTime.isoformat(), "value": data_Pressure}]}]}
        payload_data_isFall = {
            'datastreams': [{"id": "sign_fall", "datapoints": [{"at": curTime.isoformat(), "value": isFall}]}]}
        payload_data_isCure = {
            'datastreams': [{"id": "sign_sos", "datapoints": [{"at": curTime.isoformat(), "value": isCure}]}]}

        jdata_data_temperature = json.dumps(payload_data_temperature)  # 对数据进行JSON格式化编码
        jdata_data_Humidity = json.dumps(payload_data_Humidity)
        jdata_data_Pressure = json.dumps(payload_data_Pressure)
        jdata_isFall = json.dumps(payload_data_isFall)
        jdata_isCure = json.dumps(payload_data_isCure)
        # 进行上传
        requests.post(api_url, headers=apiheaders, data=jdata_data_temperature)
        requests.post(api_url, headers=apiheaders, data=jdata_data_Humidity)
        requests.post(api_url, headers=apiheaders, data=jdata_data_Pressure)
        requests.post(api_url, headers=apiheaders, data=jdata_isFall)
        requests.post(api_url, headers=apiheaders, data=jdata_isCure)

