import re
import unittest
from unittest.mock import patch
import httpretty
import json
import requests
import datetime
import dateparser

from pythainav.sources import Sec
from pythainav.nav import Nav
from .helpers.sec_data import setup_sec_data

class SecSourceTest(unittest.TestCase):

    @classmethod
    def setUp(self):
        setup_sec_data(self, httpretty)

        self.subscription_key = {'fundfactsheet': 'fact_key', 'funddailyinfo': 'daily_key'}
        self.sec = Sec(subscription_key=self.subscription_key)

        self.nav_date = datetime.date(2020,1,1)

    @classmethod
    def tearDownClass(cls):
        httpretty.disable()
        httpretty.reset()

    def test_no_subscription_key(self):
        with self.assertRaises(ValueError):
            Sec()

    def test_subscription_key_is_none(self):
        subscription_key = None
        with self.assertRaises(ValueError):
            Sec(subscription_key)

        with self.assertRaises(ValueError):
            Sec(subscription_key=subscription_key)

    def test_subscription_key_missing_key(self):

        with self.assertRaises(ValueError):
            Sec(subscription_key={'wrong_name': 'some_key'})

        with self.assertRaises(ValueError):
            Sec(subscription_key={'fundfactsheet': 'some_key'})

        with self.assertRaises(ValueError):
            Sec(subscription_key={'funddailyinfo': 'some_key'})

        test_sec = Sec(subscription_key={'fundfactsheet': 'some_key', 'funddailyinfo': 'some_key'})
        self.assertEqual(list(test_sec.subscription_key.keys()), ['fundfactsheet', 'funddailyinfo'])
        
    # 
    #   search_fund
    # 
    def test_search_fund_setting_headers(self):
        self.sec.search_fund("FUND")

        # contain Ocp-Apim-Subscription-Key in header
        self.assertTrue("Ocp-Apim-Subscription-Key" in httpretty.last_request().headers)
        self.assertEqual(httpretty.last_request().headers['Ocp-Apim-Subscription-Key'], self.subscription_key['fundfactsheet'])

    def test_search_fund_invalid_key(self):
        httpretty.reset()
        error_responses = [httpretty.Response(
            status=401,
            body=json.dumps({
                'statusCode': 401,
                'message': "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription."
            })
        )]

        httpretty.register_uri(httpretty.POST,
                            "https://api.sec.or.th/FundFactsheet/fund",
                            responses=error_responses)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.sec.search_fund("FUND")

    def test_search_fund_success_with_content(self):
        # status code 200
        result = self.sec.search_fund("FUND")

        self.assertEqual(result, self.search_fund_data)

    def test_search_fund_no_content(self):
        # status code 204
        httpretty.reset()

        httpretty.register_uri(httpretty.POST,
                            "https://api.sec.or.th/FundFactsheet/fund",
                            status=204)
        result = self.sec.search_fund("FUND")
        self.assertEqual(result, [])

    #
    #   search_class_fund
    # 
    def test_search_class_fund_setting_headers(self):
        self.sec.search_class_fund("FUND")

        # contain Ocp-Apim-Subscription-Key in header
        self.assertTrue("Ocp-Apim-Subscription-Key" in httpretty.last_request().headers)
        self.assertEqual(httpretty.last_request().headers['Ocp-Apim-Subscription-Key'], self.subscription_key['fundfactsheet'])

    def test_search_class_fund_invalid_key(self):
        httpretty.reset()
        error_responses = [httpretty.Response(
            status=401,
            body=json.dumps({
                'statusCode': 401,
                'message': "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription."
            })
        )]

        httpretty.register_uri(httpretty.POST,
                            "https://api.sec.or.th/FundFactsheet/fund/class_fund",
                            responses=error_responses)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.sec.search_class_fund("FUND")

    def test_search_class_fund_success_with_content(self):
        # status code 200
        result = self.sec.search_class_fund("FUND")

        self.assertEqual(result, self.search_class_fund_data)

    def test_search_class_fund_no_content(self):
        # status code 204
        httpretty.reset()

        httpretty.register_uri(httpretty.POST,
                            "https://api.sec.or.th/FundFactsheet/fund/class_fund",
                            status=204)
        result = self.sec.search_class_fund("FUND")
        self.assertEqual(result, [])

    #
    #   search
    # 
    @patch('pythainav.sources.Sec.search_fund')
    @patch('pythainav.sources.Sec.search_class_fund')
    def test_search_result(self, mock_search_fund, mock_search_class_fund):
        # search_fund found fund
        mock_search_fund.return_value = self.search_fund_data
        result = self.sec.search("FUND")

        self.assertEqual(result, self.search_fund_data)

        # search_fund return empty
        mock_search_fund.return_value = []
        mock_search_class_fund.return_value = self.search_class_fund_data
        result = self.sec.search("FUND")
        self.assertTrue(mock_search_class_fund.called)
        self.assertEqual(result, self.search_class_fund_data)

        # both return empty
        mock_search_fund.return_value = []
        mock_search_class_fund.return_value = []
        result = self.sec.search("FUND")
        self.assertEqual(result, [])

    #
    #   list
    # 
    def test_list_result(self):
        result = self.sec.list()

        self.assertEqual(len(result), len(self.search_fund_data))

    #
    #   get_nav_from_fund_id
    # 
    def test_get_nav_from_fund_id_setting_headers(self):
        self.sec.get_nav_from_fund_id("FUND_ID", self.nav_date)

        # contain Ocp-Apim-Subscription-Key in header
        self.assertTrue("Ocp-Apim-Subscription-Key" in httpretty.last_request().headers)
        self.assertEqual(httpretty.last_request().headers['Ocp-Apim-Subscription-Key'], self.subscription_key['funddailyinfo'])

    def test_get_nav_from_fund_id_invalid_key(self):
        httpretty.reset()
        error_responses = [httpretty.Response(
            status=401,
            body=json.dumps({
                'statusCode': 401,
                'message': "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription."
            })
        )]

        httpretty.register_uri(httpretty.GET,
                            re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
                            responses=error_responses)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.sec.get_nav_from_fund_id("FUND_ID", self.nav_date)

    def test_get_nav_from_fund_id_success_with_content(self):
        # status code 200
        expect_return = Nav(value=float(self.dailynav_data['last_val']), updated=dateparser.parse(self.dailynav_data['nav_date']), tags={}, fund="FUND_ID")

        result = self.sec.get_nav_from_fund_id("FUND_ID", self.nav_date)

        self.assertEqual(result, expect_return)

    def test_get_nav_from_fund_id_no_content(self):
        # status code 204
        httpretty.reset()

        httpretty.register_uri(httpretty.GET,
                            re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
                            status=204
        )
        result = self.sec.get_nav_from_fund_id("FUND_ID", self.nav_date)
        self.assertEqual(result, [])

    def test_get_nav_from_fund_id_multi_class(self):
        httpretty.reset()

        httpretty.register_uri(httpretty.GET,
                            re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
                            body=json.dumps(self.multi_class_dailynav_data)
        )

        fund_name = "FUND_ID"
        remark_en = self.multi_class_dailynav_data['amc_info'][0]['remark_en']
        multi_class_nav = {k.strip():float(v) for x in remark_en.split("/") for k,v in [x.split("=")]}
        expect_return = []
        for fund_name, nav_val in multi_class_nav.items():
            n = Nav(value=float(nav_val), updated=dateparser.parse(self.multi_class_dailynav_data["nav_date"]), tags={}, fund=fund_name)
            n.amount = self.multi_class_dailynav_data['net_asset']
            expect_return.append(n)

        result = self.sec.get_nav_from_fund_id(fund_name, self.nav_date)
        self.assertEqual(result, expect_return)

    #
    #   get
    # 
    def test_get_params(self):
        # date: str
        try:
            self.sec.get("FUND", self.nav_date.isoformat())
        except:
            self.fail("raise exception unexpectedly")

        # Empty Fund
        with self.assertRaises(ValueError):
            self.sec.get("", self.nav_date.isoformat())

        # date: datetime.date
        try:
            self.sec.get("FUND", self.nav_date)
        except:
            self.fail("raise exception unexpectedly")

        # date: datetime.datetime
        try:
            self.sec.get("FUND", datetime.datetime.combine(self.nav_date, datetime.datetime.min.time()))
        except:
            self.fail("raise exception unexpectedly")
