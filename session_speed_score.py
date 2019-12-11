import mysql_handler
import sys
from session_helper import *
from object_bin import *

if __name__ == '__main__':
    db = mysql_handler.MysqlHandler()
    myCursor = db.get_cursor()

    db_sessions = db.get("""SELECT ts.timeStart, ts.timeEnd, ts.id FROM tracksessions as ts
                 left join trackevents as t_events on TrackEventId = t_events.id
                 where sessionType = "Race" and SeriesId = 1;""", use_dict_cursor=True)
    try:
        if len(db_sessions) == 0:  # if there is no sessions raise exception
            raise ZeroSessionException('there is no sessions')

        betweenStr = get_sessions_date_between_str(db_sessions)
        # get all relevant session participants
        participants = get_sessions_participants(betweenStr, db)
        lapsByStartDateDict = get_sessions_by_satrte_date(participants, betweenStr, myCursor)
        sessions = create_sessions(db_sessions, lapsByStartDateDict)

        # forEach session set the worst time
        for i, v in sessions.items():
            if len(v.laps.items()) == 0:
                continue
            m = max([t[0].lapTime for l, t in v.laps.items()])
            v.worstLap = m
        print("hhh")

    except ZeroSessionException as zse:
        print(zse)
        sys.exit()
