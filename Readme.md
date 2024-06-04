**Trading Bot**
===============================

**Overview**
------------

This project is a Trading made in python. A lot of hint has been coded however all of them are not used. It was completed in 1 week !

IMPORTANT: THIS BOT IS NOT TO BE USED WITH REAL MONEY, YOU SHOULD ONLY USE IT FOR SIMULATION.

![screenshot](screenshot/gif.gif)

**Getting Started**
-------------------

To start, download the client-server interface from AiBotWorkspace and set up the location of your bot and the command line instruction. This will allow you to test your bot and see how it performs.

* Here: https://github.com/jmerle/ai-bot-workspace

### Training Data

* Three training datasets and a generator are provided alongside this subject.

### Grammar
---------

* The bot must follow a strict grammar when sending orders to the server.
* The grammar is as follows:
	+ `order = 'pass ' | trade_order`
	+ `trade_order = ('buy ' | 'sell ') currency '_' currency decimal`
	+ `currency = 'BTC ' | 'USDT '`
	+ `Orders need to be valid all the time; typically any attempt to sell more than what you own will collapse the program.`

### Server Communication
-------------------------

* The server sends general information about the game in the `info` variable.
* The first part of the data is used for training, and the second part is used for online trading.
* The bot must respond with an action within seconds, or the program will collapse and you will lose everything.

### Specification

* There is a lot of specification in this trading bot, however, here is the main tools:

- SMA
- RSA
- RSI
- EMA
- Bollinger Band
- Stop Loss system