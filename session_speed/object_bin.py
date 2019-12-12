from collections import defaultdict
from math import inf


class ZeroSessionException(Exception):
    """This exception is raised, when ther is no sessions in the db fails to start."""
    pass


class DateNullException(TypeError):
    def __init__(self, i, sessionId, startDate, endDate):
        self.index, self.sessionId, self.startDate, self.endDate = i, sessionId, startDate, endDate
        print(f"in session Id : {sessionId} start date or end date is null "
              f"startDate = {startDate} endDate = {endDate}")


class FiledSessionList(list):
    def append(self, item):
        if not isinstance(item, Session):
            raise TypeError(f"item is not of type Session")
        item = f"session id :{item.Id} have start date {item.startDate} and end date {item.endDate}\n"
        super(FiledSessionList, self).append(item)  # append the item to itself (the list)


class Lap:

    def __init__(self, lap):
        self._driver = lap[0]
        self._lapTime = lap[1]
        self._lapName = lap[2]

    @property
    def lapName(self):
        return self._lapName

    @property
    def driver(self):
        return self._driver

    @property
    def lapTime(self):
        return self._lapTime


class Session:

    def __init__(self, _id, start_date, end_date):
        self.Id = _id
        self.drivers = None
        self.laps = None
        self.startDate = start_date
        self.endDate = end_date
        self.bestLapTime = None
        self.worstLap = None

    @property
    def drivers(self):
        return self.__drivers

    @drivers.setter
    def drivers(self, driver):
        if driver is None:
            self.__drivers = list()
        else:
            self.__drivers.append(driver)

    @property
    def laps(self):
        return self.__laps

    @laps.setter
    def laps(self, lap):
        if lap is None:
            self.__laps = defaultdict(list)
        else:
            self.__laps[lap.driver].append(lap)
            self.__laps[lap.driver].sort(key=lambda _lap: _lap.lapTime, reverse=False)
            if not self.bestLapTime or lap.lapTime < self.bestLapTime:
                self.bestLapTime = lap.lapTime
