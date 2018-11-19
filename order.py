class order:
    asset = None
    currency = None
    market = None
    type = None
    limitOrder = False
    completed = False
    email = None
    equilibrium = False
    note = "Default"
    initialized = False
    orderData = {}

    def __init__(self):
        self.orderData = {}

    def getOrderData(self,key):
        if key in self.orderData:
            return self.orderData[key]
        else:
            return None
    def setOrderData(self,key,data):
        self.orderData[key] = data