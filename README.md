# TDMproposal
Python library that implements the w3c TDM proposal.


This library is now more of a draft than an alpha version. Every help will be welcomed.
The library is largely inspired by urllib.robotparser and by scrapy/protego. It implements the TDM Reservation Protocol (TDMRep), Draft Community Group Report of 05 October 2021 https://w3c.github.io/tdm-reservation-protocol/spec/

## Usage

>>> import tdmparser
>>> tdm = tdmparser.TDMParser('http://207.154.202.197/')
>>> tdm.check()
True
