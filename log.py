# -*- coding: utf-8 -*-
"""
Authors: xiaoyizong(xiaoyizong@126.com)
Date:    2015/10/21 14:00:06
"""
import logging
import logging.config

def log(level, msg):
    """
    print log,when level >= warning ,print at screen ,else in log file
    you can change the log.conf to do what you want
    Args:
         level ---the msg will be displayed in what level
                  DEBUG < INFO < WARNING < ERROR < CRITICAL
         msg  ---the msg content
    """
    logging.config.fileConfig('log.conf')
    root_logger = logging.getLogger('root')
    logger = logging.getLogger('main')

    def info(msg):
        """info"""
        root_logger.info(msg)
        logger.info(msg)

    def debug(msg):
        """debug"""
        logger.debug(msg)
        root_logger.debug(msg)

    def error(msg):
        """error"""
        logger.error(msg)
        root_logger.info(msg)

    def critical(msg):
        """critical"""
        logger.critical(msg)
        root_logger.info(msg)

    def warning(msg):
        """warning"""
        logger.warning(msg)
        root_logger.info(msg)
    funcdict = {"info":info, "debug":debug, "error":error, "critical":critical, "warning":warning}
    funcdict[level](msg)

log("warning", "W")
log("info", "I")
log("error", "E")
log("critical", "C")
log("debug", "D")
