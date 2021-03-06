####!/home/jvdeepak/anaconda3/bin/python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds

class MyOHLC(btfeeds.GenericCSVData):

      params = (
              ('fromdate', datetime.datetime(2016, 8, 1)),
              ('todate', datetime.datetime(2016, 8, 2)),
              ('nullvalue', 0.0),
              ('dtformat', ('%Y-%m-%d')),
              ('tmformat', ('%H:%M:%S')),
              ('datetime', 1),
              ('time', 2),
              ('open', 3),
              ('high', 4),
              ('low', 5),
              ('close', 6),
              ('volume', 7),
              ('openinterest', -1)
      )


# Create a Stratey
class TestStrategy(bt.Strategy):
    
    params = (
        ('maperiod', 15),
        ('printlog', True),
        ('starttimeparam', "10, 29, 59"),
    )

    def log(self, txt, dt=None, btime=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            btime = btime or self.datas[0].datetime.time(0)
            print('%s, %s, %s, %s' % (datafile._name, dt.isoformat(), btime.isoformat(), txt))
            #print('%s, %s, %s' % (dt.isoformat(), btime.isoformat(), txt))
            
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        

        # To keep track of pending orders and buy price/commision
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the high price of the series from the reference
        #self.log('High, %.2f' % self.datahigh[0])
        # Simply log the low price of the series from the reference
        #self.log('Low, %.2f' % self.datalow[0])
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])
        
        # Converting time param from string to datetime format
        starttimewithdatefrmt = datetime.datetime.strptime(self.params.starttimeparam, "%H, %M, %S")
        # Reformating datetime format to just time
        starttime = datetime.datetime.time(starttimewithdatefrmt)
        #print('%s' % starttime.isoformat())
        
        if self.datas[0].datetime.time(0) >= starttime:
            
            print('Time is xxxxxxxxxxxx')
        


            # Check if an order is pending ... if yes, we cannot send a 2nd one
            if self.order:
                return
    
            # Check if we are in the market
            if not self.position:
    
                # Not yet ... we MIGHT BUY if ...
                if self.dataclose[0] < self.dataclose[-1] < self.dataclose[-2] < self.dataclose[-3] < self.dataclose[-4] < self.dataclose[-5]:
                        # current close less than previous three closes
    
                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])
    
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()
    
            else:
    
                # Already in the market ... we might sell
                #if len(self) >= (self.bar_executed + self.params.exitbars):
                if self.dataclose[0] < self.sma[0]:
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])
    
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell()


    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)


if __name__ == '__main__':

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)
    
    # data = MyOHLC(dataname='/home/jvdeepak/data/BNF_data_1min.csv')
    datafile = MyOHLC(dataname='C:\\Users\\Deepak\\Documents\\GitHub\\backtest\\bt\\BNF_data_1min.csv')

    # Add the Data Feed to Cerebro
    cerebro.adddata(datafile, name="BNF")
    

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=2)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.000)

    # Print out the starting conditions
    #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    #cerebro.plot()
