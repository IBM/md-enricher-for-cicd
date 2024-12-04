#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def debugTimerStart():

    import time

    startTimeSection = time.time()
    return (startTimeSection)


def debugTimerEnd(self, details, description, startTimeSection):

    import time

    endTime = time.time()
    totalTime = endTime - startTimeSection
    sectionTime = str(round(totalTime, 2))
    if details['debug'] is True:
        self.log.info(self.location_name + ' ' + description + ': ' + sectionTime)
