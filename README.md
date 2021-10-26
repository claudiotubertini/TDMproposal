# TDMproposal
Python library that implements the w3c TDM proposal.


This library is now more of a draft than an alpha version and every help is welcomed. 

The library is largely inspired by urllib.robotparser and by scrapy/protego. It implements the TDM Reservation Protocol (TDMRep), Draft Community Group Report of 05 October 2021 https://w3c.github.io/tdm-reservation-protocol/spec/. 

`TDMParser.check()` tests all three ways to implement the proposal, namely, by order of importance and order in the list returned, html metadata, http header, tdmrep.json file. ~~**For the time being** the method returns all values (the presence of a license means tdm-reservation=1, False means tdm-reservation=1 and there is  no license, True means tdm-reservation=0 or there is no tdm-reservation at all).~~ The method returns the strictest result.
There is also a logging file that makes explicit all the reservation decisions made by the publisher. 

How to manage inconsistencies and unset variables is still not very clear to me, so I prefer to leave the problem to future discussions.


## Usage 
```
>>> import tdmparser 
>>> tdm = tdmparser.TDMParser('http://207.154.202.197/') 
>>> tdm.check() 
# returns the strictest result after checking among, and following the order 
stated in the proposal, the html metadata, http headers and json tdmrep.json file.
'http://207.154.202.197/license'
```
You can have a look to the logging file TDM_reservation.log that reports all relevant information about policies and reservation of the url you are scraping.

## API
```
class TDMParser  
.... 
class TDMFileParser  
.... 
class TDMHeader 
.... 
class TDMhtmlHead  
.... 
class Entry  
.... 

```
