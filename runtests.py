#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest

modules_with_tests = [
    "models.route_test"
]

def run_tests():
    sys.path.insert(0, "/usr/local/google_appengine")
    import dev_appserver
    dev_appserver.fix_sys_path()
    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromNames(modules_with_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run_tests()
