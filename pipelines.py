from AioSpider.pipelines import SqlitePipeline


class Pipeline(SqlitePipeline):
    pass


class FundListPipeline(Pipeline):
    model = 'FundListModel'


class FundPipeline(Pipeline):
    model = 'FundModel'


class FundHoldPipeline(Pipeline):
    model = 'FundHoldModel'


class StockChangePipeline(Pipeline):
    model = 'StockChangeModel'


class NetWorthPipeline(Pipeline):
    model = 'NetWorthModel'


class AccWorthPipeline(Pipeline):
    model = 'AccWorthModel'


class GrowthRatePipeline(Pipeline):
    model = 'GrowthRateModel'


class RankingPipeline(Pipeline):
    model = 'RankingModel'


class FundManagerPipeline(Pipeline):
    model = 'FundManagerModel'
