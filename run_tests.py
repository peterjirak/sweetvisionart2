# -*- coding: utf-8 -*-
import optparse
import argparse
import os
import sys
import unittest


USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules"""


def main(sdk_path, test_paths):
    if 'lib' not in sys.path:
        sys.path.insert(0, 'lib')

    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()

    suites = unittest.TestSuite()
    for test_path in test_paths:
        suite = None
        # tests/ directory
        if os.path.isdir(test_path):
            suite = unittest.loader.TestLoader().discover(test_path)
        # test_file.py
        elif os.path.isfile(test_path):
            test_path, test_file = test_path.rsplit(os.path.sep, 1)
            suite = unittest.loader.TestLoader().discover(test_path, test_file)
        # tests.module.TestCase
        elif '/' not in test_path and '.' in test_path:
            suite = unittest.loader.TestLoader().loadTestsFromName(test_path)

        if suite is not None:
            suites.addTest(suite)

    unittest.TextTestRunner(verbosity=2).run(suites)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=USAGE)
    options, args = parser.parse_args()
    if len(args) < 2:
        print 'Error: At least 2 arguments required.'
        parser.print_help()
        sys.exit(1)
    SDK_PATH = args[0]
    TEST_PATHS = args[1:]
    main(SDK_PATH, TEST_PATHS)