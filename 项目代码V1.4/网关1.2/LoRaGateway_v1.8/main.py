from dataTreating import DataTreating
import time
if __name__ == '__main__':
    data_treating = DataTreating()
    try:
        data_treating.neighborDiscovery()
        while True:
            data_treating.ReceiveData()
            data_treating.Treat()
    except Exception as ex:
        print(ex)
        data_treating.closeSerial()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
