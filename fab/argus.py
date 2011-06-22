import MySQLdb
import sys

from fabric.api import *
from pantheon import ygg

configuration = ygg.get_config()
STORAGE = '/var/lib/jenkins/jobs/argus/workspace'
WEBKIT2PNG = '/opt/pantheon/fab/webkit2png.py'
LOG = '{0}/webkit2png.log'.format(STORAGE)

def main(project,env):
    if not project:
        for p in configuration:
            with settings(warn_only=True):
                local('mkdir -p {0}/{1}'.format(STORAGE, p))
            for e in configuration[p]['environments']:
                _screenshot(p,e)
    elif project and not env:
        with settings(warn_only=True):
            local('mkdir -p {0}/{1}'.format(STORAGE, project))
        for e in configuration[project]['environments']:
            _screenshot(project,e)
    elif project and env:
        with settings(warn_only=True):
            local('mkdir -p {0}/{1}'.format(STORAGE, project))
        _screenshot(project,env)

def _screenshot(p, e):
        alias = configuration[p]['environments'][e]['apache']['ServerAlias']
        url = 'http://{0}'.format(alias)
        fname = '{0}_{1}.png'.format(p, e)
        fpath = '{0}/{1}/{2}'.format(STORAGE, p, fname)
        local('xvfb-run --server-args="-screen 0, 640x480x24" python {0} --log="{1}" {2} > {3}'.format(WEBKIT2PNG, LOG, url, fpath))

class MySQLConn(object):

    def __init__(self,username='root',password='',database=None,cursor=None):
        """Initialize generic MySQL connection object.
        If no database is specified, makes a connection with no default db.

        """
        self.connection = self._mysql_connect(database, username, password)
        self.cursor = self.connection.cursor(cursor)

    def execute(self, query, fetchall=True, warn_only=False):
        """Execute a command on the connection.

        query: SQL statement.

        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except MySQLdb.Error, e:
            self.connection.rollback()
            print "MySQL Error %d: %s" % (e.args[0], e.args[1])
            if not warn_only:
                raise
        except MySQLdb.Warning, w:
            print "MySQL Warning: %s" % (w)
        if fetchall:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchone()

    def close(self):
        """Close database connection.

        """
        self.cursor.close()
        self.connection.close()

    def _mysql_connect(self, database, username, password):
        """Return a MySQL connection object.

        """
        try:
            conn = {'host': 'localhost',
                    'user': username,
                    'passwd': password}

            if database:
                conn.update({'db': database})

            return MySQLdb.connect(**conn)

        except MySQLdb.Error, e:
            print "MySQL Error %d: %s" % (e.args[0], e.args[1])
            raise

if __name__ == '__main__':
    project = sys.argv[1] if len(sys.argv) >= 2 else None
    env = sys.argv[2] if len(sys.argv) == 3 else None
    main(project, env)
