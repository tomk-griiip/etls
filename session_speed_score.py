import mysql_handler

if __name__ == '__main__':
    db = mysql_handler.MysqlHandler()
    sessions = db.get("""SELECT * FROM tracksessions 
                         left join trackevents as t_events on TrackEventId = t_events.id
                         where sessionType = "Race" and SeriesId = 1;""", use_dict_cursor=True)
    print(len(sessions))
    print('timeEnd', sessions[0]['timeEnd'])
