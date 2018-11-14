import collections
import traceback
from abc import abstractmethod
from asyncio import sleep

import logger
import orderDataConstants
from marketBaseClass import marketBaseClass


class limitOrderMarket (marketBaseClass):
    marginFromPrice = None
    maximumDeviationFromPrice = None

    attemptsTotal = 10
    attemptsLeft = attemptsTotal
    delayBetweenAttempts = 6

    delayBetweenLimitOrder = 5

    @abstractmethod
    def closeLimitOrders(self, asset, currency):
        pass;

    @abstractmethod
    def connect(self):
        pass

    def getLimit(self, type, price, percent):
        if type == self.buyText:
            value = price * (1 + percent)
            return value
        else:
            if type == self.sellText:
                value = price * (1 - percent)
                return value


    def isInRange(self, type, firstPrice, currentPrice, percent, enabled=True):
        if enabled and currentPrice is not None:
            if type == self.buyText:
                value = self.getLimit(type, firstPrice, percent) > currentPrice
                return value
            else:
                if type == self.sellText:
                    value = self.getLimit(type, firstPrice, percent) < currentPrice
                    return value
        else:
            return True

    @abstractmethod
    def getOrderBook(self, asset, currency):
        pass

    @abstractmethod
    def extractLimitPrice(self, type, asset, currency):
        pass

    @abstractmethod
    def orderCanceled(self, orderID):
        pass



    def sendLimitOrder(self, type, asset, currency, orderQuantity, orderID, note=None, previousLimitPrice=None):

        result = collections.namedtuple('result', ['limitPrice', 'orderID'])
        res = result(previousLimitPrice, orderID)

        limitPrice = self.extractLimitPrice(type, asset, currency)

        if limitPrice != previousLimitPrice or orderID is None:
            if type == self.buyText:
                orderID = self.limitBuy(limitPrice, asset, currency, orderQuantity, orderID, note)
            else:
                if type == self.sellText:
                    orderID = self.limitSell(limitPrice, asset, currency, orderQuantity, orderID, note)

            if not self.orderCanceled(orderID):
                limitPrice = self.getOrderPrice(orderID)
                result = collections.namedtuple('result', ['limitPrice', 'orderID'])
                res = result(limitPrice, orderID)
            else:
                res = None

        if not self.orderOpen(orderID):
            res = None
        return res


    def initializeLimitOrder(self, order):
        if not order.equilibrium:
            # noinspection PyTypeChecker
            amount = abs(self.getAmountOfItem(str(order.asset)+ str(order.currency)))

        else:
            # noinspection PyTypeChecker
            amount = abs(self.getMaxAmountToUse(order.asset, order.currency) * 0.4)
        order.setOrderData('orderQuantity', amount)
        order.initialized = True

        order.setOrderData('initialPrice', self.getCurrentPrice(order.asset, order.currency))

    def makeOrder(self,order):
        try:
            if not order.initialized:
                self.initializeLimitOrder(order)

            initialPrice = order.getOrderData('initialPrice')
            previousLimitPrice = order.getOrderData('previousLimitPrice')

            order.setOrderData(orderDataConstants.orderQuantity,
                               self.quantityLeftInOrder(order.getOrderData(orderDataConstants.orderID)))

            if self.isInRange(order.type, initialPrice, previousLimitPrice, self.maximumDeviationFromPrice,
                              order.equilibrium) and order.orderQuantity != 0:
                res = self.sendLimitOrder(order.type, order.asset, order.currency, order.orderQuantity,
                                          order.getOrderData(orderDataConstants.orderID),
                                          order.note,
                                          previousLimitPrice=previousLimitPrice)
                if hasattr(res, 'orderID'):
                    order.setOrderData(orderDataConstants.orderID, res.orderID)
                    order.setOrderData(orderDataConstants.previousOrderPrice, res.limitPrice)
                else:
                    order.setOrderData(orderDataConstants.orderQuantity,
                                       self.quantityLeftInOrder(order.getOrderData(orderDataConstants.orderID),
                                                                order.getOrderData(orderDataConstants.orderQuantity)))
                    orderID = order.getOrderData(orderDataConstants.orderID)
                    order.setOrderData(orderDataConstants.orderID, None)
                    self.closeLimitOrder(orderID)
            else:
                if self.orderOpen(order.getOrderData(orderDataConstants.orderID)):
                    self.closeLimitOrder(order.getOrderData(orderDataConstants.orderID))
                self.finishOrder(order)
        except:
            tb = traceback.format_exc()
            logger.logError(tb)
            sleep(self.delayBetweenAttempts)
            self.connect()
            order.setOrderData(orderDataConstants.orderQuantity,
                               self.quantityLeftInOrder(order.getOrderData(orderDataConstants.orderID),
                                                        order.getOrderData(orderDataConstants.orderQuantity)))

    @abstractmethod
    def limitOrderStatus(self, orderID):
        pass

    @abstractmethod
    def closeLimitOrder(self, orderID):
        pass

    @abstractmethod
    def orderOpen(self, orderID):
        pass

    @abstractmethod
    def quantityLeftInOrder(self, orderID, orderQuantity):
        pass

    def finishOrder(self, order):
        if not order.equilibrium:
            order.equilibrium = True
        else:
            if not order.completed:
                order.completed = True

        logger.logCompletedOrder(self.marketName, ' Maker Limit ',
                                 order.getOrderData(orderDataConstants.previousOrderPrice),
                                 order.getOrderData(orderDataConstants.initialPrice), order.type, order.asset,
                                 order.currency, note=order.note)
        order.orderData = {}

    @abstractmethod
    def getOrderPrice(self, orderID):
        pass

    @abstractmethod
    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass

    @abstractmethod
    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass

    @abstractmethod
    def getCurrentPrice(self, asset, currency):
        pass


    @abstractmethod
    def getAmountOfItem(self, coin):
        pass


    @abstractmethod
    def getOrderBook(self, asset, currency):
        pass

    @abstractmethod
    def extractLimitPrice(self, type, asset, currency):
        pass

    @abstractmethod
    def orderCanceled(self, orderID):
        pass

    @abstractmethod
    def limitOrderStatus(self, orderID):
        pass

    @abstractmethod
    def interpretType(self, type):
        pass

    @abstractmethod
    def getMaxAmountToUse(self, asset, currency):
        pass

    @abstractmethod
    def closeLimitOrder(self, orderID):
        pass

    @abstractmethod
    def orderOpen(self, orderID):
        pass

    @abstractmethod
    def quantityLeftInOrder(self, orderID, orderQuantity):
        pass

    @abstractmethod
    def getOrderPrice(self, orderID):
        pass