from ConfigParser import ConfigParser, DuplicateSectionError
from errors import InvalidConfig


class ConfigVariable(object):

    def __init__(self, value=None):
        self.value = value

class DefaultManager(object):

    def __init__(self, config=None):
        self.config = config

    def get_default(self, section, variable):
        try:
            func_name = "%s__%s" % (section, variable)
            return getattr(self, func_name)()
        except AttributeError:
            return None

class Config(object):

    def __init__(self, config_file=None, variable_class=ConfigVariable,
        default_manager=DefaultManager()):

        super.__setattr__(self, '_config_file', config_file)
        super.__setattr__(self, '_parser', ConfigParser())
        super.__setattr__(self, '_variable_classs', variable_class)
        super.__setattr__(self, '_default_manager', default_manager)
        super.__setattr__(self, '_sections', {})

        self._default_manager.config = self
        self.add_section("Global")

        if config_file is not None:
            self._load_config()

    def add_section(self, section_name):
        self._validate_section_name(section_name)
        self._sections[section_name] = ConfigSection(name=section_name, config=self)
        try:
            self._parser.add_section(section_name)
        except DuplicateSectionError:
            pass

    def save(self, output_filename):
        with open(output_filename, 'w') as f:
            self._parser.write(f)

    def _load_config(self):
        self._parser.read(self._config_file)

        for section_name in self._parser.sections():
            self.add_section(section_name)

            for name, value in self._parser.items(section_name):
                if section_name == "Global":
                    self._validate_global_variable(name)
                self._sections[section_name].set_var(name, value)


    def _validate_section_name(self, name):
        if name[0] == '_':
            msg = "Section %s collides with a global variable of the same name."
            msg %= name
            raise InvalidConfig(msg)

        if name is not "Global" and name in self._sections['Global']:
            msg = "Section %s collides with a global variable of the same name."
            raise InvalidConfig(msg)

    def _validate_global_variable(self, name):
        if name in self._sections:
            msg = "Section %s collides with a global variable of the same name."
            raise InvalidConfig(msg)


    def __getattr__(self, name):
        try:
            return self._sections[name]
        except KeyError:
            return getattr(self._sections['Global'], name)

    def __setattr__(self, name, value):
        setattr(self._sections['Global'], name, value)


class ConfigSection(object):

    def __init__(self, name, config):
        super.__setattr__(self, '_name', name)
        super.__setattr__(self, '_variables', {})
        super.__setattr__(self, '_config', config)

    def __getattr__(self, name):
        try:
            return self._variables[name].value
        except KeyError:
            value = self._config._default_manager.get_default(section=self._name,
                variable=name)
            self.set_var(name, value)

            return self.__getattr__(name)

    def __setattr__(self, name, value):
        if not isinstance(value, self._config._variable_classs):
            value = self._config._variable_classs(value=value)

        self._variables[name] = value

    def __contains__(self, name):
        return self._variables.__contains__(name)

    def set_var(self, key, value):
        self._variables.setdefault(key, self._config._variable_classs()).value = value
        self._config._parser.set(self._name, key, value)

    def get_var(self, key):
        return self._variables[key]

