
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
        pass

    def connect(self):
        pass

    def getOrderBook(self, asset, currency):
        pass

    def extractLimitPrice(self, type, asset, currency):
        pass

    def orderCanceled(self, orderID):
        order = self.limitOrderStatus(orderID)
        if order != False:
            return order['ordStatus'] == 'Canceled'
        return True

    def limitOrderStatus(self, orderID):
        pass

    def closeLimitOrder(self, orderID):
        pass

    def orderOpen(self, orderID):
        pass

    def quantityLeftInOrder(self, orderID, orderQuantity):
        pass

    def getOrderPrice(self, orderID):
        pass

    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass

    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass

    def getCurrentPrice(self, asset, currency):
        pass

    def getAmountOfItem(self, coin):
        pass

    def interpretType(self, type):
        pass

    def getMaxAmountToUse(self, asset, currency):
        pass

# def logOrder(self, orderQuantity, asset, currency):
#     print("Available Balance: %s \n" % (self.getAvailableBalanceInUsd()))
#     print("Ordering %d contracts of %s%s \n" % (orderQuantity, asset, currency))
#     pass
#
#
#
#
#         amount = self.getAmountOfItem(asset + currency)
#         print("current amount of %s%s: %f \n" % (asset, currency, amount))
#
#         # if we are currently in a Long
#         if amount > 0:
#             amountToBuy = amount * -1
#             self.logOrder(amountToBuy, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
#             self.logOrder(amountToBuy, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
#         else:
#             # numberOfCoins = self.getNumberOfTradingPairs()
#             numberOfCoins = 2
#             allowedAmount = (self.getAvailableBalanceInUsd() / numberOfCoins)
#             extraToSell = (allowedAmount - abs(amount)) * -1
#             self.logOrder(extraToSell, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=extraToSell, ordType="Market").result()
#         pass

#
# def figureOutShare(self):
#        numberOfCoins = 2
#        availableBalance = self.getAvailableBalanceInUsd()
#        allowedAmount = availableBalance / numberOfCoins
#        extraToBuy = allowedAmount - amount
#        self.logOrder(extraToBuy, asset, currency)


# def getAvailableBalanceInUsd(self):
#     availableBalance = self.market.User.User_getMargin(currency="XBt").result()
#     user = availableBalance[0]
#     balanceInBtc = user['withdrawableMargin'] / 100000000
#     balanceInUsd = floor((balanceInBtc * self.getCurrentPrice('XBT', 'USD'))) - 1
#     return balanceInUsd
