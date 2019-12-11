from collections import defaultdict
from math import inf

class ZeroSessionException(Exception):
    """This exception is raised, when ther is no sessions in the db fails to start."""
    pass


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