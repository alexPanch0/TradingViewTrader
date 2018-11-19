# If modifying these scopes, delete the file token.json.

from gmailHandler import gmailHandler
from controller import controller
from BinanceTrader import BinanceTrader



SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


def main():

    #  CHANGE THIS TO GO FROM TESTNET TO LIVENET
    real_money = False

    trader = controller(gmailHandler('credentials.json'), .001, .1, real_money)

    trader.importAPIKeys()
    trader.run()





if __name__ == '__main__':
    main()
