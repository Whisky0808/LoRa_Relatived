import uuid
import os

def get_mac():
	mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
	print("MAC = " + mac)
	print(type(mac))
	print("%s:%s:%s:%s:%s:%s" % (mac[0:2], mac[2:4],mac[4:6], mac[6:8],mac[8:10], mac[10:]))
	transMACtoINT(mac)

def transMACtoINT(mac_str):
	mac_int = int(mac_str, 16)
	print(mac_int)
	print(type(mac_int))
	mac = hex(mac_int)
	print("now mac =  " + mac)
	mac_str = '0x' + mac_str.lower()
	print(mac_str)
	if mac == mac_str:
		print('isEqual')

if __name__ == '__main__':
	get_mac()
	os.system("pause")