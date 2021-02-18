import scrapy
from lxml import etree
from spider_project.items import ProjectItem
from spider_project import am, fm, make_item

# 获得 API
api = am.get_api('project')


class XXXSpider(scrapy.Spider):
    name = 'project'
    search_keywords = ['xxx']  # 搜索关键字

    def parse(self, response, **kwargs):
        pass

    def start_requests(self):
        """
        基于关键字开始搜索
        """
        for keyword in self.search_keywords:
            yield api.get_xxx(
                keyword=keyword,
                callback=self.parse_xxx,
            )

            yield api.post_xxx(
                start=1,
                keyword=keyword,
                callback=self.parse_yyy,
                meta={'start': 1, 'keyword': keyword}
            )

    def parse_xxx(self, response):
        """
        解析响应结果
        """
        selector = etree.HTML(response.text)

        for d in selector.xpath('//xpath1'):
            item = {
                'string': d.xpath('string(//xpath11)').text,
                'datetime': d.xpath('string(//xpath12)').text,
                'integer': d.xpath('string(//xpath13)').text,
            }
            yield make_item(item, ProjectItem)

        # 下载附件
        attachments = selector.xpath('//xpath3')
        for a in attachments:
            download_url = 'http://web' + a.attrib.get('href')
            filename = a.text
            fm.download(url=download_url, filename=filename)

    def parse_yyy(self, response):
        """
        解析响应结果
        """
        selector = etree.HTML(response.text)

        meta = response.meta
        start, keyword = meta['start'], meta['keyword']

        # 翻页，从页面里提取总页数，并与当前页数做比较
        total_records = selector.xpath('//xpath1')
        total_records = total_records.split('共')[1].split('记录')[0].strip()
        total_page = (int(total_records) - 1) // 100 + 1  # 每页有 100 个记录
        if start < total_page:
            new_meta = {'start': start + 1, 'keyword': keyword}
            yield api.get_search_result(
                start=start + 1,
                keyword=keyword,
                callback=self.parse_yyy,
                meta=new_meta
            )

        # 爬取详情
        for d in selector.xpath('//xpath2'):
            item = {
                'string': d.xpath('string(//xpath21)').text,
                'datetime': d.xpath('string(//xpath22)').text,
                'integer': d.xpath('string(//xpath23)').text,
            }
            yield make_item(item, ProjectItem)
