# -*- coding: utf-8 -*-
"""
Authors: xiaoyizong(xiaoyizong@126.com)
Date:    2015/11/16 17:23:06
"""
import chardet
import logging
import os
import Queue
import re
import socket
import sys
import threading
import time
import urllib2
import urllib

import bs4
import urlparse

import log

class  MiniSpider(threading.Thread):
    """Summary of class here.
    this mini spider will read the conf
    and crawing url
    Attributes:
        config: the config of this spider
        queue: the queue where producer putting working urls in and 
               consumer getting out.
        urlSet: the set to judge whether someone url have been crawled or not.
        rlock: a lock make some variables safe in multithreading.
        first: variable to show if this is the first time to comsume.
    """
    def __init__(self, config, queue, url_set, rlock):
        """
        initialization of the class.
        Args:
            config: config of this spider
            queue: the queue where producer putting working urls in and 
                   consumer getting out.
            urlSet: the set to judge whether someone url have been crawled or not.
            rlock: a lock make some variables safe in multithreading.

        Returns:
            None.
        """
        threading.Thread.__init__(self)
        self.config = config
        self.queue = queue
        self.urlSet = url_set
        self.rlock = rlock
        self.first = True
        urls = self.get_urls()
        for url in urls:
            if url not in self.urlSet:
                self.urlSet.add(url)
                self.queue.put((0, url))

    def get_urls(self):
        """
        get seed urls from file 
        Args:
        Returns:
            list of seed urls.
        """
        urls = []
        try:
            if os.path.exists(os.path.abspath(self.config["url_list_file"])):
                with open(self.config["url_list_file"]) as url_data:
                    datastr = url_data.readlines()
                    patt = '((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.' + \
                    '[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]' + \
                    '{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:' + \
                    '[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'
                    for urlstr in datastr:
                        urls.append(re.search(patt, urlstr).group())
                    return urls
            else:
                info = "url files not exit"
                log.log("error", info)
                return urls
        except Exception as e:
            error = 'Exception is' + str(e)
            log.log("error", error)
            return urls

    def check_coding(self, html):
        """
        turn to utf8 encoding 
        Args:
            html body within unknow encoding.

        Returns:
            utf8 encoding html body.
        """
        encoding_dict = chardet.detect(html)
        web_encoding = encoding_dict['encoding']
        if web_encoding == 'utf-8' or web_encoding == 'UTF-8':
            return html
        else:
            return html.decode('gbk', 'ignore').encode('utf-8')

    def get_html(self, url):
        """
        get html from a url 
        Args:
            url: the url string
        
        Returns:
            html body of this url.
        """
        response = None
        try:
            response = urllib2.urlopen(url, timeout = float(self.config["crawl_timeout"]))
            html = response.read()
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                error ="url is : " + url + ' Error code:' + str(e.code)
                log.log("error", error)
            elif hasattr(e, 'reason'):
                error ="url is : " + url + ' Reason:' + str(e.reason)
                log.log("error", error)
        except Exception as e:
            log.log("error", "Exception is :" + str(e))
        finally:
            if response:
                response.close()
            else:
                html = ""
        return self.check_coding(html)

    def save_targets(self, url):
        """
        save html page to file with param filename
        Args:
            url:the url string.
        Returns: none.
        """
        filepath = os.path.abspath(self.config['output'])
        log.log("info", filepath)
        if os.path.exists(filepath):
            filename = urllib.quote(url, safe=':\'/?&=()')
            filename = filename.replace(' ', '').replace(r'/', '\\')
            log.log("info", "saving url name is :" + filename)
            path = os.path.join(filepath, str(filename))
            urllib.urlretrieve(url, path)
        else:
            warning = "file path not exists,and now creating these dir:%s" % (filepath)
            log.log("warning", warning)
            try:
                makedirs(filepath)
                save_targets(filepath)
            except Exception as e:
                #single url error,do not break whole program,only print errors.
                log.log("error", str(e))

    def process_url(self, baseurl, url, depth, urlpattern):
        """
        process url to the url witch can access
        Args:
            baseurl: a baseurl for the current url.
            url: the url strings.
            depth: the depth relative to the seed url.
            urlpattern: the pattern of url.
        
        Returns:
            a url that can access directly.
	"""
        try:
            u = urllib2.urlopen(baseurl, timeout = float(self.config["crawl_timeout"]))
            #redirect 302
            baseurl = u.geturl()
            url = urlparse.urljoin(baseurl, url)
            if urlpattern.match(url):
                if url not in self.urlSet:
                    log.log("info", "add url to self.queue:" + str(url))
                    #depth + 1
                    self.queue.put((depth, url))
                    self.urlSet.add(url)
                    return url
            else:
                #javascript process
                patt = r'location.href="(.*)"'
                pattern = re.compile(patt)
                urllist = pattern.findall(url)
                if len(urllist) == 1:
                    url = urlparse.urljoin(baseurl, urllist[0])
                    if urlpattern.match(url):
                        if url not in self.urlSet:
                            log.log("info", "add url to self.queue:" + str(url))
                            self.queue.put((depth, url))
                            self.urlSet.add(url)
                            return url
                    else:
                        warning = "not a url -->" + url
                        log.log("warning", warning)
                        return url
                else:
                    warning = "do not contain a url -->" + url
                    log.log("warning", warning)
                    return url
        except Exception as e:
            error = str(e)
            log.log("error", error)
            #sys.exit(1)

    def crawl(self):
        """
        crawling main fun
        """ 
        patt = '((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z' + \
                ']{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]' + \
                '{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'
        urlpattern = re.compile(patt)
        target_pattern=re.compile(self.config["target_url"])
        while True:
            if self.queue.qsize > 0 or self.first:
                if self.rlock.acquire():
                    self.first = False
                self.rlock.release()
                #add depth process
                max_depth = int(self.config['max_depth'])
                urltuple = self.queue.get()
                depth = urltuple[0]
                url = urltuple[1]
                if depth > max_depth:
                    log.log("warning", "%s url:%s exceed max depth %s" % (self.getName(),\
                            url, max_depth))
                    self.queue.task_done()
                    continue
                info = "threadid is :" + str(self.getName()) + \
                        " is working, self.queue size is :" + str(self.queue.qsize()) + \
                        " and the working url is " + url
                log.log("info", info)
                htmlPage = self.get_html(url)
                soup = bs4.BeautifulSoup(htmlPage, "html.parser")
                if target_pattern.match(url):
                    info = "threadid is :" + str(self.ident) + " now saving url :" + str(url)
                    log.log("info", info)
                    if self.rlock.acquire():
                        self.save_targets(url)
                    self.rlock.release()
                for link in soup.select('a[href]'):
                    if link['href'] is not None:
                        self.process_url(url, link['href'], depth + 1, urlpattern)
                for img in soup.findAll("img"):
                    if img.attrs["src"] is not None:
                        self.process_url(url, img.attrs["src"], depth + 1, urlpattern)
                info = "self.queue size == " + str(self.queue.qsize()) + \
		        " , thread: " + self.getName() +" is sleeping"
                log.log("info", info)
                self.queue.task_done()
                time.sleep(float(self.config["crawl_interval"]))
            else:
                warning = "self.queue size not > 0 " + self.getName()
                log.log("warning", warning)
                time.sleep(float(self.config["crawl_interval"]))

    def run(self):
        """
        thread run function
        """
        self.crawl() 

