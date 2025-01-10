import logging
import time

def get_log(LOG_FORMAT='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            LOG_NAME='',
            LOG_FILE_INFO='engine.log',
            LOG_FILE_ERROR='engine.err'):

    timestr = time.strftime("%Y%m%d-%H%M%S")
    # LOG_FILE_INFO = 'logs/' + timestr + '.log'

    log = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)

    # comment this to suppress console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    log.addHandler(stream_handler)

    file_handler_info = logging.FileHandler(LOG_FILE_INFO, mode='w+')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    log.addHandler(file_handler_info)

    file_handler_error = logging.FileHandler(LOG_FILE_ERROR, mode='w+')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    log.addHandler(file_handler_error)

    log.setLevel(logging.INFO)

    return log
