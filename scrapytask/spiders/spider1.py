import scrapy


class ProductSpider(scrapy.Spider):
    name = "products"

    def start_requests(self):
        urls = [
            'https://mr-bricolage.bg/instrumenti/avtoaksesoari/dobavki/c/006008012'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.items)

    def items(self, response):
        for item in response.css('.product'):
            yield scrapy.Request(url='https://mr-bricolage.bg/' + item.css('.image > a').attrib['href'],
                                 callback=self.parse)
        next_page = response.css('.pagination-next a')[0].attrib['href']
        if next_page is not None:
            next_page_link = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_link, callback=self.items)

    def parse(self, response):
        specs = {}
        for row in response.css('.product-classifications > table > tbody > tr'):
            items = row.css('td::text').getall()
            specs[items[0].replace('\t', '').replace('\n', '')] = items[1].replace('\t', '').replace('\n', '')

        availability = {}
        for row in response.css('.pickup-store-list-entry'):
            key = row.css('span::text').getall()
            availability[key] = row.css('.store-availability::text')

        yield {
            'product_price': float(response.css('.js-product-price')[0].attrib['data-price-value']),
            'product_image': response.css('.test-popup-link > img')[0].attrib['src'],
            'product_title': response.css('.js-product-name::text').extract_first(),
            'product_specs': specs,
            'product_availability': availability
        }
