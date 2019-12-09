import pymysql
import traceback
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class MysqlHandler:
    # todo: CREATE CONNECTION POOL
    MAX_RETRIES = 3  # set the number of retries for executing each query

    def __init__(self):
        self.conn = None
        self.connected = False
        self.host = os.getenv('host')
        self.user = os.getenv('user')
        self.password = os.getenv('password')
        self.db_name = os.getenv('db_name')
        self.connect()
        self.connection_string = "mysql+pymysql://" + os.getenv('user') + ":" + os.getenv('password') + "@" + os.getenv(
        'host') + ":3306/" + os.getenv('db_name')

    def connect(self):
        self.conn = pymysql.connect(host=self.host,
                                    user=self.user,
                                    passwd=self.password,
                                    db=self.db_name,
                                    local_infile=1)

        self.connected = self.conn is not None
        if self.connected:
            print("Connected successfully to MYSQL\ndb schema: {}\nuser: {}".format(self.db_name, self.user))
        else:
            print("Failed to connect to MYSQL\ndb schema: {}\nuser: {}".format(self.db_name, self.user))

    def __query(self, sql, use_dict_cursor=False):
        cursor = None
        for i in range(self.MAX_RETRIES):
            try:
                if use_dict_cursor:
                    cursor = self.conn.cursor(pymysql.cursors.DictCursor)
                else:
                    cursor = self.conn.cursor()
                cursor.execute(sql)
                break
            except (pymysql.InterfaceError, pymysql.OperationalError):
                print("COULDN'T EXECUTE QUERY: {} \n RETRY ATTEMPT: {}".format(sql, i + 1))
                print(traceback.format_exc())
                cursor = None
                self.connect()

        return cursor

    def set(self, sql):
        cursor = self.__query(sql)
        if cursor is not None:
            self.conn.commit()

    def get(self, sql, use_dict_cursor=False):
        cursor = self.__query(sql, use_dict_cursor)
        return cursor.fetchall()

    def get_first(self, sql, use_dict_cursor=False):
        cursor = self.__query(sql, use_dict_cursor)
        return cursor.fetchone()

    def is_connected(self):
        return self.connected

    def get_cursor(self, use_dict_cursor=False):
        if use_dict_cursor:
            return self.conn.cursor(pymysql.cursors.DictCursor)
        else:
            return self.conn.cursor()

    def get_connection_string(self):
        return self.connection_string

mysql_handler = MysqlHandler()
