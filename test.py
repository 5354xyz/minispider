# -*- coding: utf-8 -*-
"""
Authors: xiaoyizong(xiaoyizong@126.com)
Date:    2015/07/20 17:23:06
"""
# -*- coding: utf8 -*-  
import unittest
import urllib2
import urllib
import re
import threading
import sys
import time
import Queue
import os
import logging
import argparse
import chardet
import socket

import ConfigParser
import bs4

import log
import mini_spider
import spider
import safe_utils

class TestMiniSpider(unittest.TestCase):
    """unittest class"""
    def setUp(self):
        """set up"""
        config = {}
        mini_spider.read_conf("spider.conf", config)
        thread_safe_set = safe_utils.thread_safe(set)
        urlSet = thread_safe_set()
        queue=Queue.Queue(maxsize = -1) 
        rlock = threading.RLock()
        self.spider = spider.MiniSpider(config, queue, urlSet, rlock)

    def test_readconf(self):
        """test read conf"""
        config = {}
        self.assertTrue(mini_spider.read_conf("spider.conf", config))
        self.assertFalse(mini_spider.read_conf("spider.con", config))
        self.assertFalse(mini_spider.read_conf("", config))

    def test_process_url(self):
        """test process_url"""
        baseurl = "https://www.baidu.com/"
        url = "https://www.baidu.com/"
        self.assertEqual(self.spider.process_url(baseurl, url), url)
        baseurl = "http://pycm.baidu.com:8081/"
        url = "page3.html"
        self.assertEqual(self.spider.process_url(baseurl, url), \
                "http://pycm.baidu.com:8081/page3.html")

    def test_get_urls(self):
        """test get seed urls"""
        self.spider.config["url_list_file"] = ""
        self.assertListEqual(self.spider.get_urls(), [])
        self.spider.config["url_list_file"] = "./urls"
        self.assertListEqual(self.spider.get_urls(), ["http://pycm.baidu.com:8081"])

    def test_arg_parse(self):
        """test parse"""
        extraArg = "-c spider.conf"
        res = mini_spider.arg_parse()
        self.assertEqual(mini_spider.arg_parse(), "{}")

    def test_get_html(self):
        """test get html from url"""
        urls = ["http://pycm.baidu.com:8081/page1.html", \
                "http://pycm.baidu.com:8081"]
        for url in urls:
            webPage = urllib.urlopen(url)
            html = webPage.read()
            webPage.close()
            self.assertMultiLineEqual(self.spider.get_html(url), html)

    def test_save_targets(self):
        """test save url to local file"""
        urls = ["http://www.baidu.com", "http://pycm.baidu.com:8081"]
        self.spider.config['output'] = "./output/"
        for url in urls:
            self.spider.save_targets(url)
            url = url.replace(' ', '').replace(r'/', '\\')
            self.assertTrue(os.path.exists(\
                    os.path.abspath(self.spider.config['output']) + os.path.sep + url))

    def tearDown(self):
        """teardown"""
        pass

if __name__ == '__main__':
    unittest.main()
