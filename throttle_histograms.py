"""
 classification = 'competitive'  # 'NonCompetitive'
     session_name = 'Adria R7 Race 1'
    session_id = '168'  # '161'#'193'#'169'
"""

import getopt
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import *

import mysql_handler


def print_help():
    print('-h \ --help    printing help menu')
    print('-i \ --idSession    insert session id this or nameSession is mandatory')
    print('-n \ --nameSession    insert session name this or idSession is mandatory')
    print('-c \ --classification    insert classification mandatory')
    print('--fields=    insert string of fields to query from driverlapsrundata')

    """

    :param _session_identifier: is / name
    :param classification: 'Competitive','Partial','NonCompetitive','Non-Successful','NonLegit','Verified'
    :return: 
    """


def show_plot(_session_identifier, classification):
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
    lapNames_query = "SELECT LapName FROM griiip_dev_staging.driverlaps WHERE classification = {} and lapStartDate between %s and %s".format(
        "'" + classification + "'")
    mycursor.execute(lapNames_query, (session_start_time, session_end_date))
    lapsNames = mycursor.fetchall()

    lapNamesArr = [x['LapName'] for x in lapsNames][1:10]  # create lapsNames array
    _lapNames_tuple = tuple(lapNamesArr)  # convert the array to tuple

    """
    create query to select lap name and require fields ( throttle ) from driverlapsrundata table 
    """
    runData_sql = 'SELECT throttle, lapName FROM griiip_dev_staging.driverlapsrundata where lapName IN {} order by lapName'.format(
        _lapNames_tuple)

    """
    create pandas dataFrame from the runData_sql results to be able to show on plots
    """
    sqlEngine = create_engine(db.get_connection_string()) # using sqlalchemy to query 
    dbConnection = sqlEngine.connect()
    frame = pd.read_sql(runData_sql, dbConnection)

    print("first 10 results")
    print(frame.head(10))
    print("last 10 results")
    print(frame.tail(10))

    for lap in lapNamesArr:
        subset = frame[frame['lapName'] == lap]
        # Draw the density plot
        sns.distplot(subset['throttle'], hist=False, kde=True,
                     kde_kws={'linewidth': 1},
                     label=lap)
    # Plot formatting
    plt.legend(prop={'size': 16}, title='laps')
    plt.title('Density Plot with Multiple laps')
    plt.xlabel('Delay (min)')
    plt.ylabel('Density')
    plt.show()


CLASSIFICATION_ARR = ['competitive', 'Competitive', 'Partial', 'NonCompetitive', 'Non-Successful', 'NonLegit', 'Verified']

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:n:c:h",
                                   ["idSession=", "nameSession=", "classification=", 'help', 'fields='])

    except getopt.GetoptError as go_error:
        print("getopt error : ", go_error)
        sys.exit(2)

    session_identifier = classification = fields = None
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

    show_plot(session_identifier, classification)
