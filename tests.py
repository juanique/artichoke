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
        Config(config_file)

    def test_init_default(self):
        "It can be initialized without a config file."

        config = Config()
        self.assertEqual(None, config._config_file)

    def test_load_after(self):
       "ini files can be loaded after initialization"

       config = Config()
       config.load_ini("fixtures/config1.ini")
       self.assertEqual(config.db_name, "mysql")
    
    def test_list_sections(self):
        config = Config()
        config.add_section("test2")
        config.add_section("test1")
        
        expected = [
                ('test1', config.test1),
                ('test2', config.test2)
            ]
        self.assertEqual(config.list_sections(), expected)

    def test_list_sections(self):
        config = Config()
        config.add_section("test")
        config.test.var2 = "test2"
        config.test.var1 = "test1"
        
        expected = [
                ('var1', config.test.get_var('var1')),
                ('var2', config.test.get_var('var2')),
            ]
        self.assertEqual(config.test.list_variables(), expected)
        


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
        
    def test_get_value_ci(self):
        "Values are available through case insensitive names"
        
        self.assertEqual("mysql", self.config.Global.DB_NAME)

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

    def test_is_self(self):
        "It tells whether a variable is set or not"

        self.assertEqual(True, self.config.is_set("db_name"))
        self.assertEqual(False, self.config.is_set("pony"))


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
        self.assertEquals(5, self.config.SectionA.get_var("new_var").value)

    def test_set_variable_ci(self):
        "Variables can be set through a case insensitive name, and then properly retrieved"

        self.config.SectionA.NEW_VAR = 5
        self.assertEquals(5, self.config.SectionA.get_var("new_var").value)
        self.assertEquals(5, self.config.SectionA.get_var("NEW_VAR").value)
        
    def test_del_variable(self):
        self.config.SectionA.NEW_VAR = 6
        del self.config.SectionA.NEW_VAR
        self.assertRaises(KeyError, self.config.SectionA.get_var, "new_var")

    def test_save_config(self):
        "It saves its current state to a .ini file"

        filename = "generated_config.ini"
        self.config.save(filename)

        saved_config = Config(filename)
        self.assertEquals(self.config.db_name, saved_config.db_name)
        self.assertEquals(self.config.SectionA.value_a, saved_config.SectionA.value_a)

        os.remove("generated_config.ini")

    def test_modified_init(self):
        """It detects whether any changes where made since the
        object was constructed, should be False right after __init__"""

        self.assertEquals(False, self.config.modified)

    def test_modified_after_change(self):
        "modified should be True after changing the value of a variable"

        self.config.new_var = "new_value"
        self.assertEquals(True, self.config.modified)

    def test_modified_same_vaule(self):
        """Setting a variable to the same value it had should not be considered
        a modification"""

        self.config.db_name = "mysql"
        self.assertEquals(False, self.config.modified)




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

    def test_modified_set_as_global_var(self):
        config = Config("fixtures/config1.ini")
        config.var = "value"

        self.assertFalse(config.is_set("modified"))



if __name__ == '__main__':
    unittest.main()

