'''
日志模块
'''
import logging
import os
from bbs.settings import LOGFILES_DIRS

LOG_LEVEL = logging.INFO
FILE_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def console_out(logger):
    """屏幕端输出日志信息"""
    ch = logging.StreamHandler()     # 屏幕输出
    logger.addHandler(ch)            # 绑定logger对象到ch
    ch.setFormatter(FILE_FORMATTER)  # 设置日志格式
    return logger


def file_out(logger, log_type):
    """输出日志到文件"""
    log_file_name = os.path.join(LOGFILES_DIRS, "%s.log" % log_type)  # log文件位置
    fh = logging.FileHandler(log_file_name)     # 文件输出
    fh.setLevel(LOG_LEVEL)                      # 文件输出设置等级
    logger.addHandler(fh)                       # 绑定logger对象到fh
    fh.setFormatter(FILE_FORMATTER)
    return logger


def log_handle(log_type):
    """日志处理"""
    logger = logging.getLogger(log_type)        # 定义logger
    logger.setLevel(LOG_LEVEL)         # 设定log等级

    logger = console_out(logger)                # 打印到屏幕
    logger = file_out(logger, log_type)         # 保存到file

    return logger