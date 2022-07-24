from dataTreating import DataTreating

if __name__ == '__main__':
    data_treating = DataTreating()
    try:
        while True:
            data_treating.MyTimer()
            data_treating.ReceiveData()
            data_treating.Treat()
    except Exception as ex:
        print(ex)
        data_treating.closeSerial()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
