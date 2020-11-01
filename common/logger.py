import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(self, name=__name__, file_name='calibrate', err_name='calbrate_err'):
        log_path = os.path.join(os.path.dirname(__file__), "../log")
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        logging.basicConfig()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        # 日志格式
        fmt = logging.Formatter(
            '[%(asctime)s][%(name)s][%(filename)s][line:%(lineno)d][%(levelname)s][log]: %(message)s',
            '%Y-%m-%d %H:%M:%S')

        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(logging.DEBUG)
        self.logger.addHandler(sh)

        # 将正常日志记录在file_name中，按天滚动，保存14天
        if file_name is not None:
            tf = logging.handlers.TimedRotatingFileHandler(os.path.join(log_path, file_name + ".log"),
                                                           when='D',
                                                           backupCount=14)
            tf.suffix = "%Y-%m-%d"
            tf.setFormatter(fmt)
            tf.setLevel(logging.INFO)
            self.logger.addHandler(tf)

        # 将错误日志记录在err_name中，按文件大小1G滚动，共保留14G
        if err_name is not None:
            err_handler = logging.handlers.RotatingFileHandler(os.path.join(log_path, err_name + ".log"),
                                                               mode='a',
                                                               maxBytes=1024 * 1024 * 1024,
                                                               backupCount=14)
            err_handler.setFormatter(fmt)
            err_handler.setLevel(logging.ERROR)
            self.logger.addHandler(err_handler)

    @property
    def get_log(self):
        """定义一个函数，回调logger实例"""
        return self.logger


log = Logger().get_log
