from AioSpider import models


class Model(models.SQLiteModel):
    """基类模型，仅用于继承"""

    is_delete = models.BoolField(name='逻辑删除')
    create_time = models.DateTimeField(name='创建时间')
    update_time = models.DateTimeField(name='更新时间')


class FundListModel(Model):

    name = models.CharField(
        name='基金名称', max_length=255, unique=True, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, unique=True, null=False
    )

    order = [
        'name', 'code', 'is_delete', 'create_time', 'update_time'
    ]


class FundModel(Model):

    TYPE_CHOICE = (
        ('gp', '股票型'), ('zq', '债券型'), ('zs', '指数型'), ('hh', '混合型'),
        ('lof', 'LOF'), ('fof', 'FOF'), ('etf', 'ETF'), ('qdii', 'QDII')
    )

    name = models.CharField(
        name='基金名称', max_length=255, unique=True, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, unique=True, null=False
    )
    full_name = models.CharField(
        name='基金全称', max_length=255, null=False
    )
    fund_type = models.CharField(
        name='基金类型', max_length=20, null=False, choices=TYPE_CHOICE
    )
    publish_time = models.DateTimeField(name='发行日期')
    establish_date = models.DateTimeField(name='成立日期')
    publish_copies = models.IntField(name='发行份额')
    size = models.FloatField(name='最新规模')
    now_copies = models.IntField(name='最新份额')
    fund_company = models.CharField(name='基金公司', max_length=20)
    storage_bank = models.CharField(name='托管银行', max_length=20)
    fund_manager = models.CharField(name='基金经理', max_length=20)
    bonus = models.CharField(name='基金分红', max_length=20)
    management_fee = models.FloatField(name='管理费')
    custody_fee = models.FloatField(name='托管费')
    service_fee = models.FloatField(name='服务费')
    subscript_fee = models.FloatField(name='认购费')
    purchase_fee = models.FloatField(name='认购费')
    redemption_fee = models.FloatField(name='申购费')
    baseline = models.CharField(name='业绩比较基准', max_length=20)
    track_target = models.CharField(name='跟踪标的', max_length=20)
    objectives = models.TextField(name='投资目标')
    concept = models.TextField(name='投资理念')
    range = models.TextField(name='投资范围')
    strategy = models.TextField(name='投资策略')
    dividend_policy = models.TextField(name='分红政策')
    risk_return = models.TextField(name='风险收益特征')

    order = [
        'name', 'code', 'full_name', 'fund_type',
        # 'publish_time', 'establish_date',
        'publish_copies', 'size', 'now_copies', 'fund_company', 'storage_bank', 'fund_manager',
        'bonus', 'management_fee', 'custody_fee', 'service_fee', 'subscript_fee', 'purchase_fee',
        'redemption_fee', 'baseline', 'track_target', 'objectives', 'concept', 'range',
        'strategy', 'dividend_policy', 'risk_return'
    ]


class FundHoldModel(Model):

    MARKET_CHOICE = (
        ('00', '深圳A股'), ('60', '上海A股'), ('88', '北京A股'),
        ('87', '北京A股'), ('83', '北京A股'), ('200', '深圳B股'),
        ('900', '上海B股'), ('10', '其他'), ('01', '国债'),
        ('68', '上海A股'),
    )

    name = models.CharField(
        name='基金名称', max_length=255, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, null=False
    )

    stock_name = models.CharField(
        name='持仓股票名称', max_length=255, null=False
    )
    stock_code = models.CharField(
        name='持仓股票代码', max_length=6, null=False
    )
    stock_market = models.CharField(
        name='持仓股票市场', max_length=6, null=False, choices=MARKET_CHOICE
    )

    order = [
        'name', 'code', 'stock_name', 'stock_code', 'stock_market'
    ]


class StockChangeModel(Model):

    name = models.CharField(
        name='基金名称', max_length=255, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, null=False
    )
    stamp = models.StampField(
        name='持仓日期', to_millisecond=True
    )
    proportion = models.FloatField(name='股票持仓占比')

    order = [
        'name', 'code', 'stamp', 'proportion'
    ]


class NetWorthModel(Model):

    name = models.CharField(
        name='基金名称', max_length=255, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, null=False
    )
    stamp = models.StampField(
        name='日期', to_millisecond=True
    )
    net_worth = models.FloatField(name='单位净值')
    range = models.FloatField(name='涨跌幅')

    order = [
        'name', 'code', 'stamp', 'net_worth', 'range'
    ]


class AccWorthModel(Model):

    name = models.CharField(
        name='基金名称', max_length=255, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, null=False
    )
    stamp = models.StampField(
        name='日期', to_millisecond=True
    )
    acc_worth = models.FloatField(name='累计净值')

    order = [
        'name', 'code', 'stamp', 'acc_worth'
    ]


class GrowthRateModel(Model):

    stamp = models.StampField(
        name='日期', to_millisecond=True
    )
    name = models.CharField(
        name='基金名称', max_length=255, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, null=False
    )
    growth_rate = models.FloatField(name='收益率')
    avg_same_kind = models.FloatField(name='同类平均')
    hs_300 = models.FloatField(name='沪深300')

    order = [
        'stamp', 'name', 'code', 'growth_rate', 'avg_same_kind', 'hs_300'
    ]


class RankingModel(Model):

    stamp = models.StampField(
        name='日期', to_millisecond=True
    )
    name = models.CharField(
        name='基金名称', max_length=255, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, null=False
    )
    rank = models.IntField(name='排名')
    similar_rank = models.FloatField(name='同类排名')
    percent = models.FloatField(name='同类排名占比')

    order = [
        'stamp', 'name', 'code', 'rank', 'similar_rank', 'percent'
    ]


class FundManagerModel(Model):

    name = models.CharField(
        name='基金名称', max_length=255, null=False
    )
    code = models.CharField(
        name='基金代码', max_length=6, null=False
    )
    manager_id = models.CharField(name='基金经理ID', max_length=20)
    manager_pic = models.CharField(name='基金经理头像', max_length=255)
    manager_name = models.CharField(name='基金经理姓名', max_length=20)
    manager_star = models.IntField(name='点赞数')
    work_time = models.CharField(name='从业时间', max_length=20)
    fund_size = models.CharField(name='管理规模', max_length=20)
    ability = models.FloatField(name='综合能力')
    experience_value = models.FloatField(name='经验值')
    profit_value = models.FloatField(name='收益率')
    risk_value = models.FloatField(name='抗风险')
    stability_value = models.FloatField(name='稳定性')
    timing_value = models.FloatField(name='择时能力')
    profit_rate = models.FloatField(name='任期收益')
    avg_rate = models.FloatField(name='同类平均')

    order = [
        'name', 'code', 'manager_id', 'manager_name', 'work_time', 'fund_size',
        'ability', 'experience_value', 'profit_value', 'risk_value', 'stability_value',
        'timing_value', 'profit_rate', 'avg_rate', 'manager_star', 'manager_pic',
    ]
