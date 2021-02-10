# https://healthspace.com/clients/oregon/state/statewebportal.nsf/module_healthRegions.xsp

from time import sleep

import scrapy
from scrapy_selenium import SeleniumRequest


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    start_urls = ['http://quotes.toscrape.com/']
    start_urls = ['https://healthspace.com/Clients/Oregon/Lane/Web.nsf/module_facilities.xsp?module=Food']

    def start_requests(self):
        yield SeleniumRequest(
            url=self.start_urls[0],
            wait_time=3,
            screenshot=True,
            callback=self.parse,
            dont_filter=True,
        )

    def parse(self, response):
        self.logger.info('hello this is my first spider')
        establishments = response.css('td')
        for establishment in establishments:
            bits_list = establishment.css('div').css('span::text').getall()
            yield {
                'name': establishment.css('.hidden-xs::text').get(),
                'address': bits_list[0],
                'last inspection': bits_list[1],
                'type': bits_list[2],
            }

        with open('image.png', 'wb') as image_file:
            image_file.write(response.meta['screenshot'])

        # next_page = response.css('li.pull-right div span a::attr(href)').get()
        # next_page = response.request.meta['driver'].title
        next_page = response.request.meta['driver'].find_element_by_css_selector('li.pull-right div span a')
        print(">>> next_page:", next_page)
        # next_page = response.request.meta['driver'].find_element_by_css_selector('li.pull-right div span a::attr(href)')
        next_page.click()
        sleep(3)

        if next_page is not None:
            next_page.click()
            sleep(3)
            print(">>> next_page CLICKED!")

            # next_page = response.urljoin(next_page)
            # yield scrapy.Request(next_page, callback=self.parse)
