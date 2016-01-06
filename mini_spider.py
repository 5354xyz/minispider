# -*- coding: utf-8 -*-
"""
Authors: xiaoyizong(xiaoyizong@126.com)
Date:    2015/07/20 17:23:06
"""
import argparse
import logging
import os
import Queue
import sys
import threading
import time

import ConfigParser

import log
import safe_utils
import spider


def read_conf(conf_file, config):
    """
    reading conf from config file
    Args:
        conf_file: path of config file
                   such as "home/work/xxx.cfg"
        config: witch config value will put in from the config file
    
    Returns:
        boolean value to judge whether cofig is read or not.

    """
    cf=ConfigParser.ConfigParser()
    try:
        if os.path.exists(conf_file):
            cf.read(conf_file)
            config["output"] = cf.get("spider", "output_directory")
            config["url_list_file"] = cf.get("spider", "url_list_file")
            config["max_depth"] = cf.getint("spider", "max_depth")
            config["crawl_interval"] = cf.get("spider", "crawl_interval")
            config["crawl_timeout"] = cf.get("spider", "crawl_timeout")
            config["target_url"] = cf.get("spider", "target_url")
            config["thread_count"] = cf.getint("spider", "thread_count")
            return True
        else:
            error = "config file not exits"
            log.log("error", error)
            sys.exit(1)
    except Exception as e:
        error = "config file is wrong , Exception is -->" + str(e)
        log.log("error", error)
        return False


def arg_parse():
    """
    argument Parse, if can not parse, show the usages.
    Args:
        None

    Returns:
        json string obj result of argument which is inputted by users

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf", dest="config", type=str, help="config's path of spider")
    parser.add_argument("-v", action="store_true", help="show version of mini spider")
    args = parser.parse_args()
    info = args
    log.log("info", info)
    if args.v:
        return {"version":"1.0"}
    if args.config:
        return {"config":args.config}
    usage("mini_spider.py")
    return {"error":str(args.__dict__)}


def usage(module_name):
    """
    print usage of program
    Args:
        module_name: show users how to use this module
    
    Returns:
        None.
    """
    print "Usage:"
    print "\tpython %s -c conf_file[--conf conf_file]" % module_name
    print "\tpython %s -v[--version]" % module_name
    print "\tpython %s -h[--help]" % module_name


def main(config, queue, urlSet, rlock):
    """
    starting main fun
    Args:
        config: defualt config of this spider
        queue: the queue where producer putting working urls in and 
               consumer getting out.
        urlSet: the set to judge whether someone url have been crawled or not.
        rlock: a lock make some variables safe in multithreading.

    Returns:
        None.
    """
    dic = arg_parse()
    for (k, v) in dic.items():
        if k == "version":
            print "this version is " + v
        elif k == "help":
            print "use -c config-file to boot this spider" + v
        elif k == "config":
            if read_conf(v, config):
                configstr = ', '.join([' : '.join([str(k), str(v)]) for k, v in config.items()])
                log.log("info", "config is :" + configstr)
                print "config is --->" + configstr
                log.log("info", "now starting spider~~~")
                print "now starting spider..."
                threads = []
                if config["thread_count"] > 0:
                    #TODO thread pool ???
                    for i in range(int(config["thread_count"])):
                        t = spider.MiniSpider(config, queue, urlSet, rlock)
                        threads.append(t)
                else:
                    error = "config threadcount is not a positive integer,\
                            please check your config file, exiting ..."
                    log.log("error", error)
                    sys.exit(1)
                for i in range(len(threads)):
                    log.log("info", threads[i].getName() + " is starting")
                    threads[i].setDaemon(True)
                    threads[i].start()
                print "now spidering ,please wait ~~~"
                queue.join()
                info = "now all done , and exiting"
                log.log("info", info)
                print "spider done ~~"
            else:
                error = "config read failed!"
                log.log("error", error)
                sys.exit(1)


if __name__ == '__main__':
    config = {}
    #Bloom Filters 
    thread_safe_set = safe_utils.thread_safe(set)
    urlSet = thread_safe_set()
    queue = Queue.Queue(maxsize = -1)
    rlock = threading.RLock()
    main(config, queue, urlSet, rlock)
