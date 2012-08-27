from ConfigParser import ConfigParser, DuplicateSectionError
from errors import InvalidConfig
import re


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

    def __init__(
            self, config_file=None, variable_class=ConfigVariable,
            default_manager=DefaultManager()):

        super.__setattr__(self, '_parser', ConfigParser())
        super.__setattr__(self, '_variable_classs', variable_class)
        super.__setattr__(self, '_default_manager', default_manager)
        super.__setattr__(self, '_sections', {})
        super.__setattr__(self, '_autosave', False)

        self._default_manager.config = self
        self.add_section("Global")

        if config_file is not None:
            self.load_ini(config_file)

        self.modified = False

    def autosave(self, filename):
        super.__setattr__(self, "_autosave", filename)

    def add_section(self, section_name):
        self._validate_section_name(section_name)
        if section_name not in self._sections:
            self._sections[section_name] = ConfigSection(name=section_name, config=self)
        try:
            self._parser.add_section(section_name)
        except DuplicateSectionError:
            pass

    def list_sections(self):
        sections = sorted(self._sections.items())
        return filter(lambda x: x[0] != "Global", sections)

    def save(self, output_filename):
        with open(output_filename, 'w') as f:
            self._parser.write(f)

    def load_ini(self, ini_file):
        self._parser.read(ini_file)

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
        if name == "modified":
            super.__setattr__(self, name, value)
            if self._autosave:
                self.save(self._autosave)
        else:
            setattr(self._sections['Global'], name, value)


class ConfigSection(object):

    def __init__(self, name, config):
        super.__setattr__(self, '_name', name)
        super.__setattr__(self, '_variables', {})
        super.__setattr__(self, '_config', config)

    def __getattr__(self, name):
        name = name.lower()
        try:
            value = self._variables[name].value
        except KeyError:
            value = self._config._default_manager.get_default(
                section=self._name,
                variable=name)
            self.set_var(name, value)

            return self.__getattr__(name)

        return self._parse_value(value)

    def __setattr__(self, name, value):
        name = name.lower()
        if not isinstance(value, self._config._variable_classs):
            value_var = self._config._variable_classs(value=value)
        else:
            value_var = value

        try:
            if self._variables[name].value == value_var.value:
                return
        except Exception:
            pass

        self._variables[name] = value_var

        self._config._parser.set(self._name, name, value_var.value)
        self._config.modified = True

    def __delattr__(self, name):
        del self._variables[name.lower()]
        self._config._parser.remove_option(self._name, name)

    def __contains__(self, name):
        return self._variables.__contains__(name.lower())

    def set_var(self, key, value):
        self.__setattr__(key, value)

    def get_var(self, key):
        return self._variables[key.lower()]

    def list_variables(self):
        return sorted(self._variables.items())

    def is_set(self, key):
        return key.lower() in self._variables

    def _parse_value(self, value):
        if value is None:
            return None

        try:
            if re.search("^yes$|^true$", value, re.IGNORECASE):
                return True
            if re.search("^no$|^false$", value, re.IGNORECASE):
                return False

            try:
                return int(value)
            except ValueError:
                return float(value)

        except Exception:
            return value

        return value
