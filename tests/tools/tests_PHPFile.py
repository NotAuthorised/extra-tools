# -*- coding: utf-8 -*-

import inspect
import sys
import os
import shutil
import tempfile
import unittest

current_path = os.path.abspath(inspect.getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]
sys.path.insert(0, parent_dir)
from tools import MethodData
from tools import PHPFile


# noinspection PyUnusedLocal
class TestPHPFile(unittest.TestCase):
    test_dir = None
    empty_file_path = None
    empty_class_file_path = None
    class_file_path = None
    no_file_path = None
    method_data = None

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.test_dir, 'core'))
        os.mkdir(os.path.join(self.test_dir, 'core', 'ajax'))
        os.mkdir(os.path.join(self.test_dir, 'class'))
        self.empty_file_path = self.test_dir + os.sep + 'empty.php'
        self.empty_class_file_path = self.test_dir + os.sep + 'empty_class.php'
        self.class_file_path = self.test_dir + os.sep + 'class.php'
        self.no_file_path = self.test_dir + os.sep + 'no_file.php'
        with open(self.class_file_path, 'w') as class_file:
            class_file.write('<?php\n\n')
            class_file.write('class TestPlugin\n{\n')
            class_file.write('public function testMethod()\n{\n}\n')
            class_file.write('}\n')
        with open(self.empty_class_file_path, 'w') as class_file:
            class_file.write('<?php\n\n')
            class_file.write('class EmptyClass\n{\n')
            class_file.write('}\n')
        self.method_data = MethodData()
        self.method_data.class_name = 'TestPlugin'
        self.method_data.method_name = 'testMethod'

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_method_without_file(self):
        self.method_data.class_file_path = self.test_dir + os.sep + 'no_file'
        self.assertFalse(PHPFile.add_method(self.method_data))

    def test_add_method_with_empty_file(self):
        self.method_data.class_file_path = self.test_dir + os.sep + 'empty_file'
        open(self.method_data.class_file_path, 'a').close()
        self.assertFalse(PHPFile.add_method(self.method_data))

    def test_add_method_with_only_method_in_file(self):
        self.method_data.class_file_path = self.test_dir + os.sep + 'test_file'
        with open(self.method_data.class_file_path, 'a') as test_file:
            test_file.write('testMethod()')
            test_file.close()
        self.assertFalse(PHPFile.add_method(self.method_data))

    def test_add_method_with_class_in_file(self):
        self.method_data.class_file_path = self.test_dir + os.sep + 'test_file'
        with open(self.method_data.class_file_path, 'a') as test_file:
            test_file.write('class TestPlugin {\n\n}')
            test_file.close()
        self.assertTrue(PHPFile.add_method(self.method_data))
        with open(self.method_data.class_file_path, 'r') as test_file:
            self.assertIn('function testMethod()', test_file.read())

    def test_check_class_with_empty_file(self):
        result = PHPFile.check_class(self.empty_file_path, 'TestPlugin')
        self.assertFalse(result)

    def test_check_class_without_file(self):
        result = PHPFile.check_class(self.no_file_path, 'TestPlugin')
        self.assertFalse(result)

    def test_check_class_with_class(self):
        result = PHPFile.check_class(self.class_file_path, 'TestPlugin')
        self.assertTrue(result)

    def test_check_if_method_exists_with_empty_file(self):
        result = PHPFile.check_class(self.empty_file_path, 'TestClass')
        self.assertFalse(result)

    def test_check_if_method_exists_without_file(self):
        result = PHPFile.check_class(self.no_file_path, 'TestPlugin')
        self.assertFalse(result)

    def test_check_if_method_exists_class_with_the_method(self):
        result = PHPFile.check_class(self.class_file_path, 'TestPlugin')
        self.assertTrue(result)

    def test_check_if_method_exists_class_without(self):
        result = PHPFile.check_class(self.empty_class_file_path,
                                     'TestPlugin')
        self.assertFalse(result)

    def test_write_class_with_file_doesnt_exists(self):
        result = PHPFile.write_class(self.no_file_path, 'TestPlugin')
        content = ''
        with open(self.no_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('class TestPlugin', content)
        self.assertIn('<?php', content)

    def test_write_class_with_empty(self):
        result = PHPFile.write_class(self.empty_file_path, 'TestPlugin')
        content = ''
        with open(self.empty_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('class TestPlugin', content)

    def test_write_class_with_class(self):
        result = PHPFile.write_class(self.class_file_path, 'TestClass2')
        content = ''
        with open(self.class_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('class TestPlugin', content)
        self.assertIn('class TestClass2', content)

    def test_write_method_in_class_with_empty(self):
        self.method_data.class_file_path = self.empty_file_path
        result = PHPFile.write_method_in_class(self.method_data)
        self.assertFalse(result)

    def test_write_method_in_class_without_file(self):
        self.method_data.class_file_path = self.no_file_path
        result = PHPFile.write_method_in_class(self.method_data)
        self.assertFalse(result)

    def test_write_method_in_class_with_empty_class(self):
        self.method_data.class_file_path = self.empty_class_file_path
        self.method_data.class_name = 'EmptyClass'
        result = PHPFile.write_method_in_class(self.method_data)
        content = ''
        with open(self.empty_class_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('testMethod', content)

    def test_write_method_in_class_with_not_empty_class(self):
        self.method_data.class_file_path = self.class_file_path
        self.method_data.class_name = 'TestPlugin'
        self.method_data.method_name = 'testMethod2'
        result = PHPFile.write_method_in_class(self.method_data)
        content = ''
        with open(self.class_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('testMethod', content)
        self.assertIn('testMethod2', content)

    def test_write_method_in_class_static_method(self):
        self.method_data.class_file_path = self.class_file_path
        self.method_data.method_is_static = True
        self.method_data.method_name = 'testMethod2'
        result = PHPFile.write_method_in_class(self.method_data)
        content = ''
        with open(self.class_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('static function testMethod2', content)

    def test_write_method_in_class_private_method(self):
        self.method_data.class_file_path = self.class_file_path
        self.method_data.method_visibility = 'private'
        self.method_data.method_name = 'testMethod2'
        result = PHPFile.write_method_in_class(self.method_data)
        content = ''
        with open(self.class_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('private function testMethod2', content)

    def test_write_method_in_class_protected_static_method(self):
        self.method_data.class_file_path = self.class_file_path
        self.method_data.method_is_static = True
        self.method_data.method_visibility = 'protected'
        self.method_data.method_name = 'testMethod2'
        result = PHPFile.write_method_in_class(self.method_data)
        content = ''
        with open(self.class_file_path, 'r') as file_content:
            content = file_content.read()
        self.assertTrue(result)
        self.assertIn('protected static function testMethod2', content)
