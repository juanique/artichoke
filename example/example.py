from artichoke import Config
from djangoconfig import DjangoConfigDefaultManager

config = Config(default_manager=DjangoConfigDefaultManager())
config.add_section("Database")
config.Database.db_config_name = "default"

DATABASES = {
    config.Database.db_config_name : {
        "ENGINE": config.Database.db_engine,
        "NAME": config.Database.db_name,
        "HOST": config.Database.db_user,
        "USER": config.Database.db_password,
        "PASSWORD": config.Database.db_host,
        "PORT": config.Database.db_port,
    }
}

ini_output = "local_settings.ini"
py_output = "local_settings.py"
config.save(ini_output)
with open(py_output, "w") as f:
    f.write("DATABASES = %s" % repr(DATABASES))

print "Output written to %s and %s" % (ini_output, py_output)
