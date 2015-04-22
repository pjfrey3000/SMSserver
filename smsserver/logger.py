import logging
import logging.handlers

def logger(txt):
#    print >>open(LOG_FILE, 'a'),'SMS - %17s,Unable to write PID file: %s Error %s [%s]' % (time.strftime("%Y.%m.%d %H:%M:%S"), str(PID_FILE), str(e.strerror), str(e.errno))
    print >> open(LOG_FILE, 'a'), txt

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

        