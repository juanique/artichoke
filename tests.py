from ConfigParser import ConfigParser
import unittest, os
from artichoke import Config, ConfigVariable, DefaultManager
from artichoke.errors import InvalidConfig


class ConfigUnitTestBasic(unittest.TestCase):

    def test_testsuite(self):
        self.assertEqual(2, 1+1)

    def test_init(self):
        "It can be initialized using a config file."

        config_file = "fixtures/config1.ini"
        config = Config(config_file)
        self.assertEqual(config_file, config._config_file)

    def test_init_default(self):
        "It can be initialized without a config file."

        config = Config()
        self.assertEqual(None, config._config_file)


class ConfigUnitTestLoadIni(unittest.TestCase):

    def setUp(self):
        self.config = Config("fixtures/config1.ini")

    def test_init_parse(self):
        "It parses the given .ini file using a ConfigParser"

        self.assertEqual(self.config._parser.__class__, ConfigParser)

    def test_parser_read(self):
        "The parser reads the file correctly"

        ini_value = self.config._parser.get("Global", "db_name")
        self.assertEqual("mysql", ini_value)

    def test_get_value(self):
        "It loads the values of the config file as properties."

        self.assertEqual("mysql", self.config.Global.db_name)

    def test_get_global(self):
        "It loads the [Global] variables into the object namespace."

        self.assertEqual(self.config.db_name, "mysql")

    def test_boolean_inference(self):
        "It inferes yes/no and true/false strings as boolean values."

        self.assertEqual(True, self.config.SectionA.boolean_true)
        self.assertEqual(True, self.config.SectionA.boolean_true2)
        self.assertEqual(True, self.config.SectionA.boolean_true3)
        self.assertEqual(False, self.config.SectionA.boolean_false)
        self.assertEqual(False, self.config.SectionA.boolean_false2)
        self.assertEqual(False, self.config.SectionA.boolean_false3)

    def test_number_inference(self):
        "It automatically casts integers and floats to their respective types"

        self.assertEqual(42, self.config.SectionA.fourty_two)
        self.assertEqual(42.0, self.config.SectionA.fourty_two_zero)



class ConfigUnitTestCollisions(unittest.TestCase):

    def test_config_no_underscores(self):
        "It does not allow section names to begin with an underscore."

        self.assertRaises(InvalidConfig, Config, "fixtures/underscore_section.ini")

    def test_section_name_global_collisions(self):
        "It does not allow sections names to have the same name of a global value."

        self.assertRaises(InvalidConfig, Config, "fixtures/collision.ini")

class ConfigUnitTestCreatingConfig(unittest.TestCase):

    def setUp(self):
        self.config = Config("fixtures/config1.ini")

    def test_set_section_variable(self):
        "It allow to set new config options under a specific section"

        self.config.SectionA.set_var("value_b", 3)
        self.assertEqual(3, self.config.SectionA.value_b)

    def test_set_global_variable(self):
        "It allows to set a new config option under the global section"

        self.config.global_name = "global_val"
        self.assertEqual("global_val", self.config.global_name)

    def test_add_section(self):
        "It allows to add a new section."

        self.config.add_section("SectionB")
        self.config.SectionB.set_var("value_b", 4)

        self.assertEquals(4, self.config.SectionB.value_b)

    def test_set_variable(self):
        "Variables will be setted using ConfigVariable objects"

        self.config.SectionA.new_var = 5
        self.assertTrue(isinstance(self.config.SectionA.get_var('new_var'), ConfigVariable))
        self.assertEquals(5, self.config.SectionA.get_var("new_var"). value)


    def test_save_config(self):
        "It saves its current state to a .ini file"

        filename = "generated_config.ini"
        self.config.save(filename)

        saved_config = Config(filename)
        self.assertEquals(self.config.db_name, saved_config.db_name)
        self.assertEquals(self.config.SectionA.value_a, saved_config.SectionA.value_a)

        os.remove("generated_config.ini")


class ConfigUnitTestMetaData(unittest.TestCase):

    class CustomVariable(ConfigVariable):

        def __init__(self, value):
            ConfigVariable.__init__(self, value)
            self.custom_field = "custom_value"

    class DummyDefaultManager(DefaultManager):

        def get_default(*args, **kwargs):
            return 'a'

    class FieldDefaultManager(DefaultManager):

        def SectionA__valueb(self):
            return "b"


    def test_set_var_description(self):
        "It allows to use custom Variable classes"

        config = Config(variable_class=self.CustomVariable)
        config.descriptive_var = 4
        self.assertEquals(config.get_var("descriptive_var").custom_field, "custom_value")

    def test_unset_var(self):
        "Unsetted variables have a default value of None"

        config = Config("fixtures/config1.ini")
        self.assertEquals(config.SectionA.doesnt_exists, None)


    def test_unset_default(self):
        "A default value provider can be used to manage unsetted variables."

        config = Config("fixtures/config1.ini", default_manager=self.DummyDefaultManager())
        self.assertEquals(config.SectionA.defaults_a, 'a')

    def test_unset_default_field(self):
        "The default manager can define field specific functions."

        config = Config("fixtures/config1.ini", default_manager=self.FieldDefaultManager())
        self.assertEquals(config.SectionA.valueb, "b")


class ConfigUnitTestBugs(unittest.TestCase):
    def test_setted_value_saved(self):
        "Reproduce BUG: manually asigned values ares not saved to ini file."

        config = Config("fixtures/config1.ini")
        config.SectionA.new_var = "new_value"

        filename = "generated_config.ini"
        config.save(filename)
        saved_config = Config(filename)

        self.assertEqual("new_value", saved_config.SectionA.new_var)

    def test_add_section_resets_vars(self):
        """Reproduce BUG: calling add_section() overwrittes existing
        sections with an empty one.

        """
        config = Config("fixtures/config1.ini")
        config.add_section("SectionA")

        self.assertEqual(2, config.SectionA.value_a)

if __name__ == '__main__':
    unittest.main()

