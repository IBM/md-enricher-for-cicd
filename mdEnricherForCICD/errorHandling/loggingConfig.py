#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def loggingConfig(details):

    # Send all INFO logs to the console and to the .travis.log files, but only send DEBUG logs to the .travis.log files.

    import logging
    import logging.handlers  # for the rotating file handler
    import os  # for running OS commands like changing directories or listing files in directory
    import glob

    # create log
    log = logging.getLogger(details["tool_name"])
    log.setLevel(logging.DEBUG)

    # create CONSOLE handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter for CONSOLE handler
    formatterCH = logging.Formatter('%(levelname)s: %(message)s')
    # add formatter to ch
    ch.setFormatter(formatterCH)
    # add ch to log
    log.addHandler(ch)

    if os.path.isfile(details["output_dir"] + '/.' + details["tool_name"] + '.log'):
        fileList = glob.glob(details["output_dir"] + '/.' + details["tool_name"] + '.log*')
        for filePath in fileList:
            if os.path.isfile(filePath):
                os.remove(filePath)

    # create FILE handler and set level to DEBUG
    # Github seems to have a 1MB limit on file updates, so using that as the maxBytes value
    fh = logging.handlers.RotatingFileHandler(details["output_dir"] + '/.' + details["tool_name"] + '.log', 'a',
                                              maxBytes=1000000, backupCount=75, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # create formatter for File handler
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatterFH = logging.Formatter('(%(filename)s-line %(lineno)s-%(funcName)s()) %(levelname)s: %(message)s')
    # add formatter to fh
    fh.setFormatter(formatterFH)
    # add ch to log
    log.addHandler(fh)

    return (log)
