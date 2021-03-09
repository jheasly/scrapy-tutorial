# https://github.com/Code4HR/open-health-inspection-scraper

import logging
import scrapy

logger = logging.getLogger('Healthspace Spider')

class HealthSpaceSpider(scrapy.Spider):
    name = "healthspace"
    allowed_domains = ['healthspace.com']
    start_urls = [
        'https://healthspace.com/clients/oregon/state/statewebportal.nsf/module_healthRegions.xsp?showview=region'
    ]

    def parse(self, response):
        # Initial parse of county pages
        counties = response.xpath('//tr/td')

        for county in counties:

            county_info ={
                'name': county.xpath('./a/text()').extract_first(),
                'url': county.xpath('./a/@href').extract_first(),
                'id': county.xpath('./a/@id').extract_first(),
            }

            if county_info['url']:
                # skip the county splash page
