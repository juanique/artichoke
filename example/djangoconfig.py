from artichoke import DefaultManager
from artichoke.helpers import read

class DjangoConfigDefaultManager(DefaultManager):

    def Database__db_engine(self):
        query = "Select database engine"
        options = ["postgresql_psycopg2", "postgresql", "sqlite3", "oracle", "mysql"]
        default = "mysql"

        return read(query, options=options, default=default)

    def Database__config_name(self):
        query = "Select configuration name"
        default = "default"

        return read(query, default=default)

    def Database__db_name(self):
        if self.config.Database.db_engine == 'sqlite3':
            query = "Select path to database"
            default = "/tmp/db.sqlite3"
        else:
            query = "Select database name"
            default = "django_project"

        return read(query, default=default)

    def Database__db_user(self):
        if self.config.Database.db_engine == 'sqlite3':
            return ""

        query = "Select database user"
        default = "django_user"

        return read(query, default=default)

    def Database__db_password(self):
        if self.config.Database.db_engine == 'sqlite3':
            return ""

        query = "Select database password"
        default = "django_password"

        return read(query, default=default)

    def Database__db_host(self):
        if self.config.Database.db_engine == 'sqlite3':
            return ""

        query = "Select database host"
        default = "localhost"

        return read(query, default=default)

    def Database__db_port(self):
        if self.config.Database.db_engine == 'sqlite3':
            return ""

        query = "Select database host"
        default = "%s default" % self.config.Database.db_engine

        value = read(query, default=default)
        return "" if value == default else value
