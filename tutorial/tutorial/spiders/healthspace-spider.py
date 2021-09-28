# https://github.com/Code4HR/open-health-inspection-scraper

import logging
import scrapy
from urllib import parse

from scrapy import Request

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
                county_info['url'] = parse.urljoin(county_info['url'], 'web.nsf/module_facilities.xsp?module=Food')

                yield Request(
                    county_info['url'],
                    callback=self.county_catalog_parse,
                    meta={
                        'county_info': county_info,
                        'page_num': 1,
                        'cookiejar': county_info['name'],
                    }
                )
                # each county needs a separate cookiejar so that the
                # paging works correctly in the catalog parse.


    def county_catalog_parse(self, response):
        '''
        Receives the county_info and main vendor catalog page, extracts all URLs
        from vendor page, sends each new URL to the vendor parser.
        '''

        county_info = response.meta['county_info']

        logger.info('Parsing {} Page {}'.format(county_info['name'], response.meta['page_num']))
        print('Parsing {} Page {}'.format(county_info['name'], response.meta['page_num']))

        # Check if another page is available for this county, if so send it back
        # to the parser. Uses the 'Next' button on the county page, which
        # triggers a POST request to get more vendors.
        if response.xpath('//a[contains(@id, "Next__lnk")]'):
            ajax_id = 'view:_id1:_id258:panel1'

            page_body = {
                '$$viewid': response.xpath('//form/input[@name="$$viewid"]/@value').extract_first(),
                '$$xspexecid': response.xpath('//a[contains(@id, "Next__lnk")]/parent::span/parent::div/@id').extract_first(),
                '$$xspsubmitid': response.xpath('//a[contains(@id, "Next__lnk")]/parent::span/@id').extract_first(),
                '$$xspsubmitscroll': '0|0',
                '$$xspsubmitvalue': response.xpath('//form/input[@name="$$xspsubmitvalue"]/@value').extract_first(),
            }

            # POST body includes a field that references it's own value.
            page_body[response.xpath('//form/@id').extract_first()] = response.xpath('//form/@id').extract_first()

            page_url = response.url + '&$$ajaxid=' + parse.quote('view:_id1:_id258:panel1')

            yield Request(
                response.url,
                callback=self.county_catalog_parse,
                method='POST',
                body=parse.urlencode(page_body),
                meta={
                    'county_info': county_info,
                    'page_num': response.meta['page_num']+1,
                    'cookiejar': response.meta['cookiejar'],
                },
                dont_filter=True,
            ) # Need dont_filter so the job tracker will accept the same URL
            # more than once

        # get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()
        print('>>>urls', urls)

