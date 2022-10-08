from datetime import datetime

from AioSpider import tools
from AioSpider.http import Request
from AioSpider.spider import Spider

from fundspider.models import *


class BaiduSpider(Spider):

    settings = {
        'NO_REQUEST_SLEEP_TIME': 3
    }

    start_urls = [
        'http://fund.eastmoney.com/data/rankhandler.aspx'
    ]

    def start_requests(self):

        params = {
            "op": "ph", "dt": "kf", "ft": "all", "rs": "", "gs": "0",
            "sc": "6yzf", "st": "desc", "sd": "2021-05-20", "dx": "1",
            "ed": str(datetime.now().date()), "qdii": "", "tabSubtype": ",,,,,",
            "pi": '1', "pn": "15000", "v": "0.9272696136578251"
        }

        for url in self.start_urls:
            yield Request(
                url, params=params, callback=self.parse,
                add_headers={"Referer": "http://fund.eastmoney.com"}
            )

    def parse(self, response):

        json_str = response.re('{datas:(.*),allRecords').text
        code_list = eval(json_str)

        for i in code_list[:]:
            code, name = i.split(',')[0], i.split(',')[1]

            yield FundListModel({'name': name, 'code': code})
            yield Request(
                f'http://fundf10.eastmoney.com/jbgk_{code}.html',
                callback=self.parse_fund
            )
            yield Request(
                f'http://fund.eastmoney.com/pingzhongdata/{code}.js?v={datetime.now().strftime("%Y%m%d%H%M%S")}',
                callback=self.parse_net
            )

    def fix_ttfund_response(self, response):
        # html 少了 <tr>，该方法做一个修复
        text = response.re('<table class="info w790">(.*)</table>').text
        if '</tr><th>' in text:
            response.text = response.text.replace(text, text.replace('</tr><th>', '</tr><tr><th>'))

    def parse_fund(self, response):

        self.fix_ttfund_response(response)
        table = response.xpath('//div[@class="txt_in"]//table[@class="info w790"]')
        if table.empty:
            return

        full_name = table.xpath('tr[1]/td[1]/text()').text
        name = table.xpath('tr[1]/td[2]/text()').text
        code = table.xpath('tr[2]/td[1]/text()').re(r'(\d+)').text
        _type = table.xpath('tr[2]/td[2]/text()').text
        publish_time = table.xpath('tr[3]/td[1]/text()').text
        establish_date, start_copie = table.xpath('tr[3]/td[2]/text()').text.split('/')
        start_copie = tools.str2num(start_copie, force=True, _type=float)
        size = tools.str2num(
            table.xpath('tr[4]/td[1]/text()').re('(.*?)元').extract_first(default='0', text=True),
            force=True
        )
        now_copies = tools.str2num(table.xpath('tr[4]/td[2]//text()').text, force=True)
        fund_company = table.xpath('tr[5]/td[1]//text()').text
        storage_bank = table.xpath('tr[5]/td[2]//text()').text
        fund_manager = ','.join([i for i in table.xpath('tr[6]/td[1]//text()').extract() if i != '、'])
        bonus = table.xpath('tr[6]/td[2]//text()').re(r'([\d\.]+)元').text
        management_fee = tools.str2num(table.xpath('tr[7]/td[1]/text()').text, force=True, _type=float)
        custody_fee = tools.str2num(table.xpath('tr[7]/td[2]/text()').text, force=True, _type=float)
        service_fee = tools.str2num(table.xpath('tr[8]/td[1]/text()').text, force=True, _type=float)
        subscript_fee = tools.str2num(table.xpath('tr[8]/td[2]/text()').text, force=True, _type=float)
        purchase_fee = tools.str2num(table.xpath('tr[9]/td[1]/text()').text, force=True, _type=float)
        redemption_fee = tools.str2num(table.xpath('tr[9]/td[2]/text()').text, force=True, _type=float)
        performance_baseline = table.xpath('tr[10]/td[1]//text()').text
        track_target = table.xpath('tr[10]/td[2]/text()').text

        objectives = response.xpath('//div[@class="txt_in"]/div[2]/div/p/text()').strip_text()
        concept = response.xpath('//div[@class="txt_in"]/div[3]/div/p/text()').strip_text()
        _range = response.xpath('//div[@class="txt_in"]/div[4]/div/p/text()').strip_text()
        strategy = response.xpath('//div[@class="txt_in"]/div[5]/div/p/text()').strip_text()
        dividend_policy = response.xpath('//div[@class="txt_in"]/div[6]/div/p/text()').strip_text()
        risk_return = response.xpath('//div[@class="txt_in"]/div[7]/div/p/text()').strip_text()

        if 'FOF' in name:
            _type = 'fof'
        elif 'LOF' in name:
            _type = 'lof'
        elif '债券型' in _type:
            _type = 'zq'
        elif '指数型' in _type:
            _type = 'zs'
        elif '混合' in _type:
            _type = 'hh'
        elif '股票型' in _type:
            _type = 'gp'
        elif 'qdii' in _type.lower():
            _type = 'qdii'
        else:
            _type = _type

        yield FundModel({
            'name': name, 'code': code, 'full_name': full_name, 'fund_type': _type, 'publish_time': publish_time,
            'establish_date': establish_date, 'publish_copies': start_copie, 'size': size, 'now_copies': now_copies,
            'fund_company': fund_company, 'storage_bank': storage_bank, 'fund_manager': fund_manager,
            'bonus': bonus, 'management_fee': management_fee, 'custody_fee': custody_fee, 'service_fee': service_fee,
            'subscript_fee': subscript_fee, 'purchase_fee': purchase_fee, 'redemption_fee': redemption_fee,
            'baseline': performance_baseline, 'track_target': track_target, 'objectives': objectives,
            'concept': concept, 'range': _range, 'strategy': strategy, 'dividend_policy': dividend_policy,
            'risk_return': risk_return
        })

    def parse_net(self, response):

        name = response.re('var fS_name.?=.?"(.*?)";').text
        code = response.re('var fS_code.?=.?"(.*?)";').text

        # 现费率、最小申购金额
        charge = response.re('var fund_Rate.?=.?"(.*?)";').extract_first(default='0', text=True)
        fund_min_money = response.re('var fund_minsg.?=.?"(.*?)";').extract_first(default='0', text=True)
        charge = tools.str2num(char=charge, force=True, _type=float)
        fund_min_money = tools.str2num(char=fund_min_money, force=True, _type=float)

        # 近一年收益率、近6月收益率、近三月收益率、近一月收益率
        syl_1n = response.re('var syl_1n.?=.*?"(.*?)";').extract_first(default='0', text=True)
        syl_6y = response.re('var syl_6y.?=.*?"(.*?)";').extract_first(default='0', text=True)
        syl_3y = response.re('var syl_3y.?=.*?"(.*?)";').extract_first(default='0', text=True)
        syl_1y = response.re('var syl_1y.?=.*?"(.*?)";').extract_first(default='0', text=True)

        syl_1n = tools.str2num(char=syl_1n, force=True, multi=0.01, _type=float)
        syl_6y = tools.str2num(char=syl_6y, force=True, multi=0.01, _type=float)
        syl_3y = tools.str2num(char=syl_3y, force=True, multi=0.01, _type=float)
        syl_1y = tools.str2num(char=syl_1y, force=True, multi=0.01, _type=float)

        # 基金持仓股票代码、基金持仓债券代码
        stock_codes = response.re('var stockCodes=(.*?);').extract_first(default='[]', text=True)
        zq_codes = response.re('var zqCodes.?=.?(.*?);').text
        stock_codes = tools.load_json(stock_codes, default=[])
        zq_codes = tools.type_converter(zq_codes, to=str, force=True)
        zq_codes = [i for i in zq_codes.split(',') if i]

        # 股票仓位测算图、单位净值走势、累计净值走势、累计收益率走势
        fund_stock_positions = response.re('var Data_fundSharesPositions.?=.?(.*?);').extract_first(default='[]', text=True)
        net_worth_trend = response.re('var Data_netWorthTrend.?=.?(.*?);').extract_first(default='[]', text=True)
        ac_worth_trend = response.re('var Data_ACWorthTrend.?=.?(.*?);').extract_first(default='[]', text=True)
        grand_total = response.re('var Data_grandTotal.?=.?(.*?);').extract_first(default='[]', text=True)
        fund_stock_positions = tools.load_json(fund_stock_positions, default=[])
        net_worth_trend = tools.load_json(net_worth_trend, default=[])
        ac_worth_trend = tools.load_json(ac_worth_trend, default=[])
        grand_total = tools.load_json(grand_total, default=[])

        # 同类排名走势、同类排名百分比、现任基金经理
        rate_similar_type = response.re('var Data_rateInSimilarType.?=.?(.*?);').extract_first(default='[]', text=True)
        rate_similar_persent = response.re('var Data_rateInSimilarPersent.?=(.*?);').extract_first(default='[]', text=True)
        fund_manager = response.re('var Data_currentFundManager.?=(.*?);').text
        rate_similar_type = tools.load_json(rate_similar_type, default=[])
        rate_similar_persent = tools.load_json(rate_similar_persent, default=[])
        fund_manager = tools.load_json(fund_manager, default=[])

        for i in stock_codes + zq_codes:

            if i[:2] == '01':
                market = '01'
            elif i[0:3] == '30':
                market = '00'
            elif i[0:3] == ['900', '200']:
                market = i[1:4]
            elif i[0:2] in ['00', '60', '83', '87', '88']:
                market = i[0:2]
            elif i[0:2] == '68':
                market = '68'
            else:
                market = '10'

            yield FundHoldModel({
                'name': name, 'code': code, 'stock_name': '', 'stock_code': i[:-1],
                'stock_market': market
            })

        for a, b in fund_stock_positions:
            yield StockChangeModel({
                'name': name, 'code': code, 'stamp': a, 'proportion': b
            })

        for i in net_worth_trend:
            yield NetWorthModel({
                'name': name, 'code': code, 'stamp': i['x'], 'net_worth': i['y'], 'range': i['equityReturn']
            })

        for a, b in ac_worth_trend:
            yield AccWorthModel({
                'name': name, 'code': code, 'stamp': a, 'acc_worth': tools.type_converter(b, to=float, force=True)
            })

        if grand_total:
            time_list = [i[0] for i in grand_total[0]['data']]
            growth_list = [i[1] for i in grand_total[0]['data']]
            avg_list = [i[1] for i in grand_total[1]['data']]
            hs300_list = [i[1] for i in grand_total[2]['data']]

            for a, b, c, d in zip(time_list, growth_list, avg_list, hs300_list):
                yield GrowthRateModel({
                    'name': name, 'code': code, 'stamp': a, 'growth_rate': b, 'avg_same_kind': c, 'hs_300': d
                })

        rank_time_list = [i['x'] for i in rate_similar_type]
        rank_list = [i['y'] for i in rate_similar_type]
        sim_rank_list = [tools.type_converter(i['sc'], to=float, force=True) for i in rate_similar_type]
        percent_list = [i[1] for i in rate_similar_persent]

        for a, b, c, d in zip(rank_time_list, rank_list, sim_rank_list, percent_list):
            yield RankingModel({
                'name': name, 'code': code, 'stamp': a, 'rank': b, 'similar_rank': c, 'percent': d
            })

        for manager in fund_manager:
            yield FundManagerModel({
                'name': name, 'code': code,
                'manager_id': tools.parse_json(manager, 'id', ''),
                'manager_pic': tools.parse_json(manager, 'pic', ''),
                'manager_name': tools.parse_json(manager, 'name', ''),
                'manager_star': tools.parse_json(manager, 'star', 0),
                'work_time':  tools.parse_json(manager, 'workTime', ''),
                'fund_size':  tools.parse_json(manager, 'fundSize', ''),
                'experience_value':  tools.type_converter(
                    tools.parse_json(manager, 'power.data[0]', 0), to=float, force=True
                ),
                'profit_value':  tools.type_converter(
                    tools.parse_json(manager, 'power.data[1]', 0), to=float, force=True
                ),
                'risk_value':  tools.type_converter(
                    tools.parse_json(manager, 'power.data[2]', 0), to=float, force=True
                ),
                'stability_value':  tools.type_converter(
                    tools.parse_json(manager, 'power.data[3]', 0), to=float, force=True
                ),
                'timing_value':  tools.type_converter(
                    tools.parse_json(manager, 'power.data[4]', 0), to=float, force=True
                ),
                'ability': tools.type_converter(tools.parse_json(manager, 'power.avr', 0), to=float, force=True),
                'profit_rate': tools.parse_json(manager, 'profit.series[0].data[0].y', ''),
                'avg_rate': tools.parse_json(manager, 'profit.series[0].data[1].y', ''),
            })


if __name__ == '__main__':
    import asyncio
    spider = BaiduSpider()
    spider.start()
