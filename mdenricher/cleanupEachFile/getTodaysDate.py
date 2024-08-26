def getTodaysDate():

    from datetime import datetime

    now = datetime.now()
    currentYear = str(now.year)
    currentMonth = str(now.month)
    currentDay = str(now.day)
    if len(currentMonth) == 1:
        currentMonth = '0' + currentMonth
    if len(currentDay) == 1:
        currentDay = '0' + currentDay

    return (currentYear, currentMonth, currentDay)
