from datetime import datetime

import pytest
import pandas as pd

from decimal import Decimal

from iexfinance.stocks import (get_historical_data, get_sector_performance,
                               get_collections, get_crypto_quotes,
                               get_todays_earnings, get_ipo_calendar,
                               get_historical_intraday, Stock)
from iexfinance.utils.exceptions import IEXSymbolError, IEXEndpointError


class TestBase(object):

    def test_wrong_iex_input_type(self):
        with pytest.raises(ValueError):
            Stock(34)
        with pytest.raises(ValueError):
            Stock("")
        with pytest.raises(ValueError):
            ls = []
            Stock(ls)

    def test_symbol_list_too_long(self):
        with pytest.raises(ValueError):
            x = ["tsla"] * 102
            Stock(x)


class TestShareDefault(object):

    def setup_class(self):
        self.cshare = Stock("AAPL")
        self.cshare2 = Stock("AAPL", output_format='pandas')
        self.cshare3 = Stock("SVXY")
        self.cshare4 = Stock("AAPL",
                             json_parse_int=Decimal,
                             json_parse_float=Decimal)
        self.cshare5 = Stock("GIG^")

    @pytest.mark.xfail(reason="Unstable.")
    @pytest.mark.legacy
    def test_invalid_symbol(self):
        data = Stock("BAD SYMBOL")
        with pytest.raises(IEXSymbolError):
            data.get_price()

    def test_get_endpoints(self):
        data = self.cshare.get_endpoints(["price"])
        assert list(data) == ["price"]

    def test_get_endpoints_bad_endpoint(self):
        with pytest.raises(IEXEndpointError):
            self.cshare.get_endpoints(["BAD ENDPOINT", "quote"])

        with pytest.raises(IEXEndpointError):
            self.cshare.get_endpoints("BAD ENDPOINT")

    def test_get_chart_params(self):
        data = self.cshare.get_chart()
        # Test chart ranges
        data2 = self.cshare.get_chart(range='1y')
        assert 15 < len(data) < 35
        assert 240 < len(data2) < 260

        # Test chartSimplify
        data4 = self.cshare.get_chart(chartSimplify=True)[0]
        assert "simplifyFactor" in list(data4)

        data5 = self.cshare.get_chart(range='1y', chartInterval=5)
        assert 45 < len(data5) < 55

    @pytest.mark.xfail(reason="This test only runs correctly between 00:00 and"
                       "09:30 EST")
    def test_get_chart_reset(self):
        # Test chartReset
        data3 = self.cshare.get_chart(range='1d', chartReset=True)
        assert data3 == []

    def test_get_dividends_params(self):
        data = self.cshare.get_dividends()
        data2 = self.cshare.get_dividends(range='2y')
        data3 = self.cshare.get_dividends(range='5y')
        assert len(data) < len(data2) < len(data3)

    @pytest.mark.xfail(reason="Provider error. Awaiting patch.")
    def test_get_news_params(self):
        data = self.cshare.get_news(last=15)
        assert len(data) == 15

    def test_get_quote_params(self):
        data = self.cshare.get_quote()
        data2 = self.cshare.get_quote(displayPercent=True)

        assert (abs(data2["ytdChange"]) >
                abs(data["ytdChange"]))

    def test_get_splits_params(self):
        afl = Stock("AAPL")
        data = afl.get_splits(range="1m")
        data2 = afl.get_splits(range="5y")
        assert len(data2) > len(data)

    def test_filter(self):
        data = self.cshare.get_quote(filter_='ytdChange')
        assert isinstance(data, dict)
        assert isinstance(data["ytdChange"], (int, float))

        data4 = self.cshare4.get_quote(filter_='ytdChange')
        assert isinstance(data4, dict)
        assert isinstance(data4["ytdChange"], Decimal)


class TestBatchDefault(object):

    def setup_class(self):
        self.cbatch = Stock(["aapl", "tsla"])
        self.cbatch2 = Stock(["aapl", "tsla"], output_format='pandas')
        self.cbatch3 = Stock(["uvxy", "svxy"])

    def test_invalid_symbol_or_symbols(self):
        with pytest.raises(IEXSymbolError):
            a = Stock(["TSLA", "BAD SYMBOL", "BAD SYMBOL"])
            a.get_price()

    def test_get_endpoints(self):
        data = self.cbatch.get_endpoints(["price"])["AAPL"]
        assert list(data) == ["price"]

    def test_get_endpoints_bad_endpoint(self):
        with pytest.raises(IEXEndpointError):
            self.cbatch.get_endpoints(["BAD ENDPOINT", "quote"])

        with pytest.raises(IEXEndpointError):
            self.cbatch.get_endpoints("BAD ENDPOINT")

    @pytest.mark.legacy
    def test_get_all(self):
        data = self.cbatch.get_all()
        assert len(data) == 2
        assert len(data["AAPL"]) == 20

    def test_get_chart_params(self):
        data = self.cbatch.get_chart()["AAPL"]
        # Test chart ranges
        data2 = self.cbatch.get_chart(range='1y')["AAPL"]
        assert 15 < len(data) < 35
        assert 240 < len(data2) < 260

        # Test chartSimplify
        data4 = self.cbatch.get_chart(chartSimplify=True)["AAPL"][0]
        assert "simplifyFactor" in list(data4)

        data5 = self.cbatch.get_chart(range='1y', chartInterval=5)["AAPL"]
        assert 45 < len(data5) < 55

    @pytest.mark.xfail(reason="This test only works overnight")
    def test_get_chart_reset(self):
        # Test chartReset
        data = self.cbatch.get_chart(range='1d', chartReset=True)
        assert data == []

    def test_get_dividends_params(self):
        data = self.cbatch.get_dividends()["AAPL"]
        data2 = self.cbatch.get_dividends(range='2y')["AAPL"]
        data3 = self.cbatch.get_dividends(range='5y')["AAPL"]
        assert len(data) < len(data2) < len(data3)

    def test_get_quote_format(self):
        data = self.cbatch.get_quote()
        data2 = self.cbatch.get_quote(displayPercent=True)
        assert (abs(data2["AAPL"]["ytdChange"]) >
                abs(data["AAPL"]["ytdChange"]))

    def test_get_select_ep_bad_params(self):
        with pytest.raises(IEXEndpointError):
            self.cbatch.get_endpoints()

        with pytest.raises(IEXEndpointError):
            self.cbatch.get_endpoints("BADENDPOINT")


class TestHistorical(object):

    def setup_class(self):
        self.good_start = datetime(2017, 2, 9)
        self.good_end = datetime(2017, 5, 24)

    def test_single_historical_json(self):

        f = get_historical_data("AMZN", self.good_start, self.good_end)
        assert isinstance(f, dict)
        assert len(f) == 73

        expected1 = f["2017-02-09"]
        assert expected1["close"] == pytest.approx(821.36, 3)
        assert expected1["high"] == pytest.approx(825.0, 3)

        expected2 = f["2017-05-24"]
        assert expected2["close"] == pytest.approx(980.35, 3)
        assert expected2["high"] == pytest.approx(981.0, 3)

    def test_single_historical_pandas(self):

        f = get_historical_data("AMZN", self.good_start, self.good_end,
                                output_format="pandas")

        assert isinstance(f, pd.DataFrame)
        assert isinstance(f.index, pd.DatetimeIndex)
        assert len(f) == 73

        expected1 = f.loc["2017-02-09"]
        assert expected1["close"] == pytest.approx(821.36, 3)
        assert expected1["high"] == pytest.approx(825.0, 3)

        expected2 = f.loc["2017-05-24"]
        assert expected2["close"] == pytest.approx(980.35, 3)
        assert expected2["high"] == pytest.approx(981.0, 3)

    def test_batch_historical_json(self):

        f = get_historical_data(["AMZN", "TSLA"], self.good_start,
                                self.good_end, output_format="json")

        assert isinstance(f, dict)
        assert len(f) == 2
        assert sorted(list(f)) == ["AMZN", "TSLA"]

        a = f["AMZN"]
        t = f["TSLA"]

        assert len(a) == 73
        assert len(t) == 73

        expected1 = a["2017-02-09"]
        assert expected1["close"] == pytest.approx(821.36, 3)
        assert expected1["high"] == pytest.approx(825.0, 3)

        expected2 = a["2017-05-24"]
        assert expected2["close"] == pytest.approx(980.35, 3)
        assert expected2["high"] == pytest.approx(981.0, 3)

        expected1 = t["2017-02-09"]
        assert expected1["close"] == pytest.approx(269.20, 3)
        assert expected1["high"] == pytest.approx(271.18, 3)

        expected2 = t["2017-05-24"]
        assert expected2["close"] == pytest.approx(310.22, 3)
        assert expected2["high"] == pytest.approx(311.0, 3)

    def test_batch_historical_pandas(self):

        f = get_historical_data(["AMZN", "TSLA"], self.good_start,
                                self.good_end, output_format="pandas")

        assert isinstance(f, pd.DataFrame)
        assert len(f) == 73
        assert sorted(list(f.columns.levels[0])) == ["AMZN", "TSLA"]

        a = f["AMZN"]
        t = f["TSLA"]

        assert len(a) == 73
        assert len(t) == 73

        expected1 = a.loc["2017-02-09"]
        assert expected1["close"] == pytest.approx(821.36, 3)
        assert expected1["high"] == pytest.approx(825.0, 3)

        expected2 = a.loc["2017-05-24"]
        assert expected2["close"] == pytest.approx(980.35, 3)
        assert expected2["high"] == pytest.approx(981.0, 3)

        expected1 = t.loc["2017-02-09"]
        assert expected1["close"] == pytest.approx(269.20, 3)
        assert expected1["high"] == pytest.approx(271.18, 3)

        expected2 = t.loc["2017-05-24"]
        assert expected2["close"] == pytest.approx(310.22, 3)
        assert expected2["high"] == pytest.approx(311.0, 3)

    def test_invalid_dates(self):
        start = datetime(2010, 5, 9)
        end = datetime(2017, 5, 9)
        with pytest.raises(ValueError):
            get_historical_data("AAPL", start, end)

    def test_invalid_dates_batch(self):
        start = datetime(2010, 5, 9)
        end = datetime(2017, 5, 9)
        with pytest.raises(ValueError):
            get_historical_data(["AAPL", "TSLA"], start, end)

    def test_invalid_symbol_batch(self):
        start = datetime(2017, 2, 9)
        end = datetime(2017, 5, 24)
        with pytest.raises(IEXSymbolError):
            get_historical_data(["BADSYMBOL", "TSLA"], start, end)


@pytest.mark.legacy
class TestCrypto(object):

    def setup_class(self):
        self.ticks = ["BTCUSDT", "EOSUSDT", "ETHUSDT", "BNBUSDT", "ONTUSDT",
                      "BCCUSDT", "ADAUSDT", "XRPUSDT", "TUSDUSDT", "TRXUSDT",
                      "LTCUSDT", "ETCUSDT", "IOTAUSDT", "ICXUSDT", "NEOUSDT",
                      "VENUSDT", "XLMUSDT", "QTUMUSDT"]

    def test_listed_crypto_symbols(self):
        a = Stock(self.ticks)
        assert isinstance(a.get_quote(), dict)

    def test_get_crypto_quotes(self):
        data = get_crypto_quotes()
        assert isinstance(data, list)

    def test_get_cypto_quotes_pandas(self):
        data = get_crypto_quotes(output_format='pandas')
        assert isinstance(data, pd.DataFrame)

        assert len(data) == 43
        assert data.loc["sector"][0] == "cryptocurrency"


class TestSectorPerformance(object):

    def test_list_sector_performance(self):
        li = get_sector_performance()
        assert len(li) == pytest.approx(10, 1)


@pytest.mark.cloudbroken
@pytest.mark.xfail(reason="Provider issue")
class TestCollections(object):

    def test_get_collections_no_collection(self):
        with pytest.raises(TypeError):
            get_collections()

        with pytest.raises(ValueError):
            get_collections("Computer Hardware", "badcollection")

    def test_get_collections(self):
        data = get_collections("Computer Hardware")

        assert isinstance(data, list)
        assert len(data) > 100

    def test_get_collections_pandas(self):
        df = get_collections("Computer Hardware", output_format='pandas')

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 39

        assert "change" in df.index
        assert "close" in df.index

    def test_get_collections_type(self):
        df = get_collections("Industrials", "sector", output_format='pandas')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 39
        assert len(df.columns) > 500


class TestTodaysEarnings(object):

    def test_get_todays_earnings(self):
        data = get_todays_earnings()

        assert isinstance(data, dict)
        assert "bto" in data
        assert "amc" in data


class TestIPOCalendar(object):

    def test_get_ipo_calendar_default(self):
        data = get_ipo_calendar()

        assert isinstance(data, dict)
        assert set(data) == set(["rawData", "viewData"])

        assert isinstance(data["rawData"], list)
        assert isinstance(data["viewData"], list)

    def test_get_ipo_calendar_today(self):
        data = get_ipo_calendar("today-ipos")

        assert isinstance(data, dict)
        assert len(data) == 3
        assert "lastUpdate" in data

    def test_ipo_calendar_bad_period(self):
        with pytest.raises(ValueError):
            get_ipo_calendar("BADPERIOD")


class TestHistoricalIntraday(object):

    def verify_timeframe(self, data):
        assert data.index[0].hour == 9
        assert data.index[0].minute == 30
        assert data.index[-1].hour == 15
        assert data.index[-1].minute == 59

    def test_intraday_fails_no_symbol(self):
        with pytest.raises(TypeError):
            get_historical_intraday()

    def test_intraday_default(self):
        data = get_historical_intraday("AAPL")

        assert isinstance(data, list)

    def test_intraday_pandas(self):
        data = get_historical_intraday("AAPL", output_format='pandas')

        assert isinstance(data, pd.DataFrame)
        assert isinstance(data.index, pd.DatetimeIndex)

        self.verify_timeframe(data)

    def test_intraday_pandas_pass_datetime(self):
        u_date = "20190415"
        data = get_historical_intraday("AAPL", date=u_date,
                                       output_format='pandas')

        assert isinstance(data, pd.DataFrame)
        assert data.index[0].strftime("%Y%m%d") == u_date

        self.verify_timeframe(data)

    def test_intraday_pass_date_str(self):
        data = get_historical_intraday("AAPL", date="20190415")

        assert isinstance(data, list)

    def test_intraday_pass_datetime(self):
        date = datetime(2018, 10, 27)

        data = get_historical_intraday("AAPL", date=date)

        assert isinstance(data, list)
