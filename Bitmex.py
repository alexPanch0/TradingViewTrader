import datetime
from decimal import Decimal
from math import floor
from time import sleep

import bitmexApi.bitmex
import logger
from limitOrderMarket import limitOrderMarket


# a controller for ONE bitmex connection. This is a basic formula for how it should look.
class Bitmex(limitOrderMarket):
    def closeLimitOrders(self, asset, currency):
        # client.Order.Order_cancel(orderID='').result()
        self.market.Order.Order_cancelAll().result()

    def connect(self):
        self.market = bitmexApi.bitmex.bitmex(test=not self.real_money, config=None, api_key=self.apiKey,
                                              api_secret=self.apiKeySecret)

    def getOrderBook(self, asset, currency):
        res = self.market.OrderBook.OrderBook_getL2(symbol=asset + currency).result()[0]
        return res

    def extractLimitPrice(self, type, asset, currency):
        orderBook = self.getOrderBook(asset, currency)

        limitPrice = -5

        if type == self.buyText:
            limitPrice = 0
        else:
            if type == self.sellText:
                limitPrice = 999999

        for order in orderBook:

            if self.buyText.lower() == order['side'].lower():
                if order['price'] > limitPrice:
                    limitPrice = order['price']
            else:
                if self.sellText.lower() == order['side'].lower():
                    if order['price'] < limitPrice:
                        limitPrice = order['price']
        return limitPrice

    def orderCanceled(self, orderID):
        order = self.limitOrderStatus(orderID)
        if order != False:
            return order['ordStatus'] == 'Canceled'
        return True

    def limitOrderStatus(self, orderID,triesLeft = None):
        if triesLeft == None:
            triesLeft = 1
        if orderID == None:
            return False
        filter = '{"orderID": "' + orderID + '"}'
        res = self.market.Order.Order_getOrders(filter=filter).result()

        try:
            res = res[0][0]
            status = res['ordStatus']
        except:
            if triesLeft != 0:
                sleep(1)
                return self.limitOrderStatus(orderID)
            triesLeft = triesLeft - 1
            logger.logError('--- ORDER LIST ERROR ---')

        return res

    def closeLimitOrder(self, orderID):
        if orderID != None:
            res = self.market.Order.Order_cancel(orderID=orderID).result()
            return res
        else:
            return None

    def interpretType(self, type):
        if type.lower() == 'LONG'.lower():
            return self.buyText
        else:
            if type.lower() == 'SHORT'.lower():
                return self.sellText
            else:
                if type.lower() == 'u18':
                    return 'Z18'
        return type

    def orderOpen(self, orderID):
        if orderID == None:
            return False
        order = self.limitOrderStatus(orderID)
        status = order['ordStatus']
        one = order['ordStatus'] != 'Canceled'
        two = order['ordStatus'] != 'Filled'
        return one and two

    def quantityLeftInOrder(self, orderID, orderQuantity):
        if orderID == None:
            return orderQuantity
        else:
            status = self.limitOrderStatus(orderID)
            return status['orderQty'] - status['cumQty']

    def getOrderPrice(self, orderID):
        order = self.limitOrderStatus(orderID)
        if order is not None:
            return order['price']
        return None

    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderId=None, note=None):
        result = None

        openOrder = self.orderOpen(orderId)
        if openOrder and orderQuantity != 0:
            result = self.market.Order.Order_amend(orderID=orderId, price=limitPrice).result()
            logger.logOrder(self.marketName, 'Limit', limitPrice, asset, currency, orderQuantity,
                            str(note) + ' amend for order: ' + str(orderId))
        if not openOrder and orderQuantity != 0:
            result = self.market.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, ordType="Limit",
                                                 price=limitPrice, execInst='ParticipateDoNotInitiate').result()
            logger.logOrder(self.marketName, 'Limit', limitPrice, asset, currency, orderQuantity, note)

        if result is not None:
            print('Rate limit is now: ' + self.getRemainingRequests(result))
            # print('Rate limit is now: ' + str(result[1]['headers']['_store']['x-ratelimit-remaining']))
            tradeInfo = result[0]
            for key, value in tradeInfo.items():
                if key == "orderID":
                    newOrderId = (key + ": {0}".format(value))
                    return newOrderId[9:]
        else:
            return None

    def getRemainingRequests(self,result):
        item = result[1].headers.get('x-ratelimit-remaining')
        return item

    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        return self.limitBuy(limitPrice, asset, currency, -orderQuantity, orderNumber, note)


    def getCurrentPrice(self, asset, currency):
        trades = self.market.Trade.Trade_get(symbol=asset + currency, count=4, reverse=True).result()
        sum = 0
        volume = 0
        for trade in trades[0]:
            sum = sum + (trade['price'] * trade['size'])
            volume = volume + trade['size']
        strRes = sum / volume
        strRes = str(strRes)
        return float(strRes)

    def getAmountOfItem(self, coin):
        if coin.lower() == 'xbt':
            return self.market.User.User_getMargin().result()[0]['availableMargin'] / self.btcToSatoshi
        else:
            symbol = '{"symbol": "' + coin + '"}'
            result = self.market.Position.Position_get(filter=symbol).result()
            if len(result[0]) > 0:
                return result[0][0]['currentQty']
            else:
                return 0

    def interpretType(self, type):
        if type.lower() == 'LONG'.lower():
            return self.buyText
        else:
            if type.lower() == 'SHORT'.lower():
                return self.sellText
            else:
                if type.lower() == 'u18':
                    return 'Z18'
        return type

    def getMaxAmountToUse(self, asset, currency,curr = None):
        percentLower = 0.01
        if curr is None:
            curr = self.getAmountOfItem('XBt') * (1 - percentLower)

        price = self.getCurrentPrice(asset, currency)
        if currency == 'USD' or (currency == 'Z18' and asset == 'XBT'):
            result = floor(curr * price)
        else:
            result = floor((curr / price))
        return result
