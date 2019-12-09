import mysql_handler
if __name__ == '__main__':
    db = mysql_handler.MysqlHandler()
    sessions = db.get("""SELECT * FROM griiip_dev_staging.tracksessions 
                         left join griiip_dev_staging.trackevents on TrackEventId = griiip_dev_staging.trackevents.id 
                         where sessionType = "Race" and SeriesId = 1;""",use_dict_cursor=True)
    print('timeEnd', sessions[0]['timeEnd'])