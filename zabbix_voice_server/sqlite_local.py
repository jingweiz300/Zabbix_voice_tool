import sqlite3
import re
import os
class sqldb(object):
    def __init__(self):
        if os.path.exists('db'):
            os.remove('db')
        self.sqlcon = sqlite3.connect("file:memDB1?mode=memory&cache=shared",check_same_thread=False, uri=True)
        #self.sqlcon = sqlite3.connect('db',check_same_thread=False)
        self.sqlcur = self.sqlcon.cursor()
    def _insert(self,tablename,values):
        sql_query = 'insert into {0} values {1}'.format(tablename,values)
        c = re.compile('None')
        sql_query = c.sub("' '", sql_query)
        self.sqlcur.execute(sql_query)
        self.sqlcon.commit()
    def _select(self,sql):
        self.sqlcur.execute(sql)
        results = self.sqlcur.fetchall()
        self.sqlcon.commit()
        return results
    def _execute(self,sql):
        self.sqlcur.execute(sql)

