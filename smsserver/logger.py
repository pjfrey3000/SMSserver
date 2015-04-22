import logging
import logging.handlers

def openlog(LOG_FILE):
    logger = logging.getLogger("smsserver")
    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024000, backupCount=5)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler) 
    logger.setLevel(logging.INFO)
    return(logger)

def writelog(logger,txt,level):
    if level == "error":
        logger.error(txt)
    if level == "warning":
        logger.warning(txt)
    if level == "info":
        logger.info(txt)
    if level == "debug":
        logger.debug(txt)

        