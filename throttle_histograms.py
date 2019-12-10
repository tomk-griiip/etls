"""
 classification = 'competitive'  # 'NonCompetitive'
     session_name = 'Adria R7 Race 1'
    session_id = '168'  # '161'#'193'#'169'
"""

import getopt
import sys
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import *
import statistics
import mysql_handler


def print_help():
    print('-h \\ --help    printing help menu')
    print('-i \\ --idSession    insert session id this or nameSession is mandatory')
    print('-n \\ --nameSession    insert session name this or idSession is mandatory')
    print('-c \\ --classification    insert classification mandatory')
    print('-r \\ --remote    use this when execute the script from remote server')
    print('-l \\ --legend   add legend to the plot')
    print('--hist \\ if add to the commend --hist histogram will be shown on the plot')
    print('--fields=    insert string of fields to query from driverlapsrundata')

    """

    :param _session_identifier: is / name
    :param classification: 'Competitive','Partial','NonCompetitive','Non-Successful','NonLegit','Verified'
    :return: 
    """


def show_plot(_session_identifier, _classification, _remote=False, _hist=False, _legend=False):
    """
    if script run from remote server allow x11 forwarding
    """
    if _remote:
        matplotlib.use('tkagg')

    """
        init mysql instance
    """
    db = mysql_handler.MysqlHandler()
    mycursor = db.get_cursor(True)

    """
    query session by _session_identifier
    """
    sessions_query = """SELECT * FROM griiip_dev_staging.tracksessions WHERE {}""".format(_session_identifier)
    mycursor.execute(sessions_query)
    session = mycursor.fetchone()

    session_start_time = session['timeStart']  # session start date
    session_end_date = session['timeEnd']  # session end date

    """
    query lap name from driverlaps table that was in the relevant session by the end and start date of the session
    """
    lapNames_query = "SELECT lapName, lapTime FROM griiip_dev_staging.driverlaps WHERE classification = {} and lapStartDate between %s and %s".format(
        "'" + _classification + "'")
    mycursor.execute(lapNames_query, (session_start_time, session_end_date))
    laps_from_driverLaps = mycursor.fetchall()
    lapsDict = {lap['lapName']: str(lap['lapTime']) for lap in laps_from_driverLaps}
    lapNames = [x['lapName'] for x in laps_from_driverLaps]
    if _remote is False:
        lapNames = lapNames[1:10]  # create laps_from_driverLaps array
    _lapNames_tuple = tuple(lapNames)  # convert the array to tuple

    if len(lapNames) == 0:
        raise Exception('there is no laps in that session and _classification')
    """
    create query to select lap name and require fields ( throttle ) from driverlapsrundata table 
    """
    runData_sql_for_dataFrame = 'SELECT throttle, lapName FROM griiip_dev_staging.driverlapsrundata where lapName IN {} order by lapName'.format(
        _lapNames_tuple)

    """
    create pandas dataFrame from the runData_sql_for_dataFrame results to be able to show on plots
    """
    sqlEngine = create_engine(db.get_connection_string())  # using sqlalchemy to query
    dbConnection = sqlEngine.connect()
    frame = pd.read_sql(runData_sql_for_dataFrame, dbConnection)

    """
    log all laps with the lap time 
    """
    print('laps logs:')
    print(*lapsDict.items(), sep='\n')

    for lap in lapNames:
        subset = frame[frame['lapName'] == lap]
        # Draw the density plot
        if _legend:
            sns.distplot(subset['throttle'], hist=_hist, kde=True,
                         kde_kws={'linewidth': 1}, label=lap)
            plt.legend(prop={'size': 16}, title='laps')
        else:
            sns.distplot(subset['throttle'], hist=_hist, kde=True,
                         kde_kws={'linewidth': 1})
        # ,label=lap)

    plt.title('Density Plot with Multiple laps')
    plt.xlabel('throttle')
    plt.ylabel('num of laps')
    # fig = plt.figure()
    # fig.savefig('temp.png', transparent=True)
    plt.show()


CLASSIFICATION_ARR = ['competitive', 'Competitive', 'Partial', 'NonCompetitive', 'Non-Successful', 'NonLegit',
                      'Verified']

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:n:c:h:l:r",
                                   ["idSession=", "nameSession=", "classification=", 'help', 'legend', 'remote', 'hist', 'fields='])

    except getopt.GetoptError as go_error:
        print("getopt error : ", go_error)
        sys.exit(2)

    session_identifier = classification = fields = None
    legend = hist = remote = False
    for opt, arg in opts:
        if opt in ('-i', '--idSession'):
            session_identifier = 'id = ' + arg

        elif opt in ('-n', '--nameSession'):
            session_identifier = 'name = ' + arg

        if opt in ('-c', '--classification'):
            if arg not in CLASSIFICATION_ARR:
                print('-c \ --classification need to be ont of the above \n Competitive, Partial, NonCompetitive, '
                      'Non-Successful, NonLegit, Verified')
                sys.exit(0)

            classification = arg

        if opt in '--fields':
            fields = arg

        if opt in ('-h', '--help'):
            print_help()
            sys.exit(0)
        if opt in ('-r', '--remote'):
            remote = True
        if opt in '--hist':
            hist = True
        if opt in ('-l', '--legend'):
            legend = True

    try:
        show_plot(session_identifier, classification, remote, hist, legend)
    except Exception as e:
        print(e)
        sys.exit()
