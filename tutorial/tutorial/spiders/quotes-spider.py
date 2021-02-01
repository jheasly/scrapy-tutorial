# https://healthspace.com/clients/oregon/state/statewebportal.nsf/module_healthRegions.xsp

import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    start_urls = ['http://quotes.toscrape.com/']
    start_urls = ['https://healthspace.com/Clients/Oregon/Lane/Web.nsf/module_facilities.xsp?module=Food']

    def parse(self, response):
        self.logger.info('hello this is my first spider')
        establishments = response.css('td')
        for establishment in establishments:
            yield {
                'name': establishment.css('.hidden-xs::text').get(),
                'bits': establishment.css('div').css('span::text').getall(),
            }

# response.css('td').css('.hidden-xs::text').get()