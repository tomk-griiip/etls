from operator import itemgetter
from itertools import groupby
from session_speed.object_bin import *


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
    lapTime_userId_query = """ select lapStartDate, userId, lapTime, lapName from driverlaps 
                                where classification = 'competitive' 
                                and {}
                                and UserId in {} order by UserId""".format(betweenStr, tuple(participants))

    myCursor.execute(lapTime_userId_query)
    laps = myCursor.fetchall()
    test = groupby(laps, itemgetter(0))
    # return {v[0]: (v[1], v[2], v[3]) for v in laps}
    return laps
    #return dict((k, [(v[1], v[2], v[3]) for v in itr]) for k, itr in groupby(laps, itemgetter(0)))


def write_to_file(file, lst):
    with open(file, 'w+') as fp:
        for line in lst:
            fp.write(line)


def create_sessions(_db_sessions, _laps_by_start_date_dict):
    _sessions = defaultdict(Session)
    sessionsWithoutTime = FiledSessionList()
    for s in _db_sessions:
        sessionId = s['id']
        if sessionId not in _sessions.keys():
            session = Session(sessionId, s['timeStart'], s['timeEnd'])
            is_date_missing = session.startDate is None or session.endDate is None
            if is_date_missing:
                sessionsWithoutTime.append(session)
                continue
        else:
            session = _sessions[sessionId]
        for d in _laps_by_start_date_dict:#.keys():
            if session.startDate < d[0] < session.endDate:
                _lap = Lap(d)#_laps_by_start_date_dict[d][0])
                session.laps = _lap
                if _lap.driver not in session.drivers:
                    session.drivers = _lap.driver
        _sessions[session.Id] = session
    if len(sessionsWithoutTime) > 0:
        write_to_file('filed_sessions.txt', sessionsWithoutTime)
    return _sessions


def calculate_session_avg_score(driverAvgLap, sessionBestLap, sessionWorst2Lap):
    try:
        return ((1 - ((driverAvgLap - sessionBestLap) / (sessionWorst2Lap - sessionBestLap))) * 80) + 20
    except ZeroDivisionError as ze:
        print(f"avg error : ({driverAvgLap} - {sessionBestLap}) / ({sessionWorst2Lap} - {sessionBestLap})")
        return 100


def calculate_session_best_score(driverBestLap, sessionBestLap, sessionWorstLap):
    try:
        return ((1 - ((driverBestLap - sessionBestLap) / (sessionWorstLap - sessionBestLap))) * 80) + 20
    except ZeroDivisionError as ze:
        print(f"best : {driverBestLap} - {sessionBestLap} ' / ' {sessionWorstLap} - {sessionBestLap})")
        return 100
