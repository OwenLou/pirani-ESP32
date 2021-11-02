class avgFiter():
    """
    滑动平均滤波
    """
    def __init__(self, dataList=None, dataListLen=8):
        if dataListLen < 2:
            dataLen = 2  # 强制最小平滑数目
        if dataList == None:
            self.dataSum = 0
            self.dataLen = dataListLen
            self.dataList = [0 * dataListLen]
        else:
            self.dataSum = sum(dataList)
            self.dataList = dataList
            self.dataLen = len(dataList)
    def fit(self, data):
        # 因为一般是整形, 所以如下操作是安全的
        self.dataSum = self.dataSum - self.dataList[0] + data
        self.dataList.pop(0)
        self.dataList.append(data)
        data = self.dataSum / self.dataLen
        return data