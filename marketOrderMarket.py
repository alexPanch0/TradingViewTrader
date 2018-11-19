import traceback
from abc import abstractmethod
from asyncio import sleep

import bank
import logger
from marketBaseClass import marketBaseClass


class marketOrderMarket(marketBaseClass):
    limitOrderEnabled = False

    @abstractmethod
    def getCurrentPrice(self, asset, currency):
        pass;


    def marketOrder(self, type, asset, currency):
        try:
            currentAmount = self.getAmountOfItem(asset + currency)
            text = "current amount of %s%s: %f \n  %s" % (asset, currency, currentAmount, type)
            print(text)
            bank.logNote(text)

            change = self.resetToEquilibrium_Market(currentAmount, asset, currency)
            bank.logBalance(self.getAmountOfItem('xbt'))
            orderSize = self.getMaxAmountToUse(asset, currency) * 0.4
            if type == self.buyText:
                result = self.marketBuy(orderSize, asset, currency, note='Going long.. Previous round trip profit')
                bank.logContract(asset, currency, self.getAmountOfItem(asset + currency))
            else:
                if type == self.sellText:
                    result = self.marketSell(orderSize, asset, currency, note='Going short')
                    bank.logContract(asset, currency, self.getAmountOfItem(asset + currency))
            self.attemptsLeft = self.attemptsTotal
            return True
        except:
            tb = traceback.format_exc()
            logger.logError(tb)
            if self.attemptsLeft == 0:
                self.attemptsLeft = self.attemptsTotal
                return None
            sleep(self.delayBetweenAttempts)
            self.connect()
            self.attemptsLeft = self.attemptsLeft - 1
            self.marketOrder(type, asset, currency)



    @abstractmethod
    def marketBuy(self, orderSize, asset, currency, note):
        pass

    @abstractmethod
    def marketSell(self, orderSize, asset, currency, note):
        pass

