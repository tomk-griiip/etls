from collections import defaultdict
from operator import itemgetter
from itertools import groupby
from object_bin import *


class ZeroSessionException(Exception):
    """This exception is raised, when ther is no sessions in the db fails to start."""
    pass


def get_sessions_date_between_str(db_sessions):
    """
        create array of or lapStartDate between statement
        """
    list_between = ["or lapStartDate between '" + str(t['timeStart']) + "' and '" + str(t['timeEnd']) + "'" for t in
                    db_sessions]
    """
        create string from the list_between array with the query for the lapStartDate between  where clause 
        """
    last_index = len(list_between) - 1
    list_between[0] = list_between[0].replace('or', '(')
    list_between[last_index] += ')'
    return ' '.join(map(str, list_between))


def get_sessions_participants(betweenStr, db):
    sessions_participants_query = """select sessionparticipants.userId from sessionparticipants left join (select ts.id from tracksessions as ts left join trackevents as t_events on TrackEventId = t_events.id 
                                where sessionType = "Race" and SeriesId = 1) as tse on sessionId = tse.id group by sessionparticipants.userId;"""

    participants_tuple = db.get(sessions_participants_query)  # get participants (as tuple)
    return [item for t in participants_tuple for item in
            t]  # convert list of tuple participants to list of participants


def get_sessions_by_satrte_date(participants, betweenStr, myCursor):
    """
    select users relevant laps time
    """
    lapTime_userId_query = """ select lapStartDate, userId, lapTime, lapName from grip_test_new.driverlaps 
                                where classification = 'competitive' 
                                and {}
                                and UserId in {} order by UserId""".format(betweenStr, tuple(participants))

    myCursor.execute(lapTime_userId_query)
    laps = myCursor.fetchall()
    return dict((k, [(v[1], v[2], v[3]) for v in itr]) for k, itr in groupby(laps, itemgetter(0)))


def create_sessions(_db_sessions, _laps_by_start_date_dict):
    _sessions = defaultdict(Session)
    for s in _db_sessions:
        sessionId = s['id']
        if sessionId not in _sessions.keys():
            session = Session(sessionId, s['timeStart'], s['timeEnd'])
        else:
            session = _sessions[sessionId]
        for d in _laps_by_start_date_dict.keys():
            if session.startDate < d < session.endDate:
                _lap = Lap(_laps_by_start_date_dict[d][0])
                session.laps = _lap
                if _lap.driver not in session.drivers:
                    session.drivers = _lap.driver
        _sessions[session.Id] = session

    return _sessions
