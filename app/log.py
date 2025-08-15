import logging
import os

logger = logging.getLogger('fcs_share_service')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(message)s")

fileHandler = logging.FileHandler(os.path.join('logs', 'fcs-share-service.log'))
fileHandler.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(ch)
