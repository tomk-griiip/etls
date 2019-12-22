from datetime import datetime
from functools import reduce

import mysql_handler
import sys
from session_speed.session_helper import *
from session_speed.object_bin import *
import os
import operator

if __name__ == '__main__':
    db = mysql_handler.MysqlHandler()
    myCursor = db.get_cursor()

    db_sessions = db.get("""SELECT ts.timeStart, ts.timeEnd, ts.id FROM tracksessions as ts
                 left join trackevents as t_events on TrackEventId = t_events.id
                 where sessionType = "Race" and SeriesId = 1""", use_dict_cursor=True)
    try:
        if len(db_sessions) == 0:  # if there is no sessions raise exception
            raise ZeroSessionException('there is no sessions')

        betweenStr = get_sessions_date_between_str(db_sessions)
        # get all relevant session participants
        participants = get_sessions_participants(betweenStr, db)
        lapsByStartDateDict = get_sessions_by_satrte_date(participants, betweenStr, myCursor)
        sessions = create_sessions(db_sessions, lapsByStartDateDict)

        # forEach session set the best time of the worst driver (session.worstLap)
        for i, v in sessions.items():
            if len(v.laps.items()) == 0:
                continue
            m = max([t[0].lapTime for l, t in v.laps.items()])
            v.worstLap = m
        print("creating insert into sql file ")

        useStr = f"use {os.getenv('db_name')};\n"
        bestSpeedInsertInToList = list([useStr])
        avgSpeedInsertInToList = list([useStr])
        for sessionId, session in sessions.items():
            lapsByDriver = session.laps
            for driver in session.drivers:
                lapsLst = lapsByDriver[driver]
                lapsTime = [t.lapTime for t in lapsLst]
                _sum = reduce(operator.add, [t.lapTime for t in lapsLst])
                driverAvg = (_sum / len(lapsLst))
                driverBestLap, sessionBestLap, sessionWorstLap = lapsLst[0], \
                                                                 session.bestLapTime, \
                                                                 session.worstLap
                bestScore = calculate_session_best_score(driverBestLap.lapTime,
                                                         sessionBestLap,
                                                         sessionWorstLap)
                avgScore = calculate_session_best_score(driverAvg,
                                                        sessionBestLap,
                                                        session.worstWorstLap)
                bestSpeedInsertInTo = f"insert into driverscoringhistory (userId, TrackSessionId, sessionSpeedScore)" \
                                      f"values({driver}, {sessionId},{bestScore}) ON DUPLICATE KEY UPDATE " \
                                      f"sessionSpeedScore = {bestScore};\n"

                avgSpeedInsertInTo = f"insert into driverscoringhistory (userId, TrackSessionId, sessionPerformanceScore)" \
                                      f"values({driver}, {sessionId},{avgScore}) ON DUPLICATE KEY UPDATE " \
                                     f"sessionPerformanceScore = {avgScore};\n"
                bestSpeedInsertInToList.append(bestSpeedInsertInTo)
                avgSpeedInsertInToList.append(avgSpeedInsertInTo)
        print("writing to file ...")

        write_to_file('sessionSpeedScore.sql', bestSpeedInsertInToList)
        write_to_file('sessionPerformanceScore.sql', avgSpeedInsertInToList)
        print("done")
    except ZeroSessionException as zse:
        print(zse)
        sys.exit()
