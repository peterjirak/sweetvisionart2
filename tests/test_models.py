import re
from datetime import datetime

import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from models.user import User


class ModelTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_adding_and_getting_users(self):
        alan_turing_inst1 = User.add_or_get_user(google_user_id=911222837233357812345, email='Alan.Turing@test.com',
                                                 first_name='Alan', last_name='Turing')
        alan_turing_inst2 = None
        alan_turing_application_user_id = alan_turing_inst1.application_user_id

        if alan_turing_application_user_id is not None and not re.match(r"^\s*$", alan_turing_application_user_id):
            alan_turing_inst2 = User.get_user_by_application_user_id(alan_turing_application_user_id)

        alan_turing_inst3 = User.get_user_by_google_user_id(911222837233357812345)

        ada_lovelace_inst1 = User.add_or_get_user(google_user_id=922333108122260921438, email='Ada.Lovelace@test.com',
                                                  first_name='Ada', last_name='Lovelace')
        ada_lovelace_inst2 = None
        ada_lovelace_application_user_id = ada_lovelace_inst1.application_user_id

        if ada_lovelace_application_user_id is not None and not re.match(r"^\s*$", ada_lovelace_application_user_id):
            ada_lovelace_inst2 = User.get_user_by_application_user_id(ada_lovelace_application_user_id)

        ada_lovelace_inst3 = User.get_user_by_google_user_id(922333108122260921438)

        george_boole_inst1 = User.add_or_get_user(google_user_id=933444263033301235672, email='George.Boole@test.com',
                                                  first_name='George', last_name='Boole')

        george_boole_inst2 = None
        george_boole_application_user_id = george_boole_inst1.application_user_id

        if george_boole_application_user_id is not None and not re.match(r"^\s*$", george_boole_application_user_id):
            george_boole_inst2 = User.get_user_by_application_user_id(george_boole_application_user_id)

        george_boole_inst3 = User.get_user_by_google_user_id(933444263033301235672)

        jean_bartik_inst1 = User.add_or_get_user(google_user_id=900111072122302041980, email='Jean.Bartik@test.com',
                                                 first_name='Jean', last_name='Bartik')

        jean_bartik_inst2 = None
        jean_bartik_application_user_id = jean_bartik_inst1.application_user_id

        if jean_bartik_application_user_id is not None and not re.match(r"^\s*$", jean_bartik_application_user_id):
           jean_bartik_inst2 = User.get_user_by_application_user_id(jean_bartik_application_user_id)

        jean_bartik_inst3 = User.get_user_by_google_user_id(900111072122302041980)

        self.assertEqual(alan_turing_inst1.first_name, 'Alan')
        self.assertEqual(alan_turing_inst1.last_name, 'Turing')
        self.assertEqual(alan_turing_inst1.email, 'Alan.Turing@test.com')
        self.assertEqual(alan_turing_inst1.google_user_id, '911222837233357812345')
        self.assertRegexpMatches(alan_turing_inst1.application_user_id, r"^[A-Za-z0-9][A-Za-z0-9\-]+[A-Za-z0-9]+$")
        self.assertTrue(isinstance(alan_turing_inst1.created_at, datetime))

        self.assertEqual(ada_lovelace_inst1.first_name, 'Ada')
        self.assertEqual(ada_lovelace_inst1.last_name, 'Lovelace')
        self.assertEqual(ada_lovelace_inst1.email, 'Ada.Lovelace@test.com')
        self.assertEqual(ada_lovelace_inst1.google_user_id, '922333108122260921438')
        self.assertRegexpMatches(ada_lovelace_inst1.application_user_id, r"^[A-Za-z0-9][A-Za-z0-9\-]+[A-Za-z0-9]+$")
        self.assertTrue(isinstance(ada_lovelace_inst1.created_at, datetime))

        self.assertEqual(alan_turing_inst1, alan_turing_inst3)
        self.assertEqual(ada_lovelace_inst1, ada_lovelace_inst3)
        self.assertEqual(george_boole_inst1, george_boole_inst3)
        self.assertEqual(jean_bartik_inst1, jean_bartik_inst3)

        if alan_turing_application_user_id is not None and not re.match(r"^\s*$", alan_turing_application_user_id):
            self.assertEqual(alan_turing_inst1, alan_turing_inst2)
        else:
            self.fail("A valid application_user_id was not generated for User Alan Turing")

        if ada_lovelace_application_user_id is not None and not re.match(r"^\s*$", ada_lovelace_application_user_id):
            self.assertEqual(ada_lovelace_inst2, ada_lovelace_inst1)
        else:
            self.fail("A valid application_user_id was not generated for User Ada Lovelace")

        if george_boole_application_user_id is not None and not re.match(r"^\s*$", george_boole_application_user_id):
            self.assertEqual(george_boole_inst2, george_boole_inst1)
        else:
            self.fail("A valid application_user_id was not generated for User George Boole")

        if jean_bartik_application_user_id is not None and not re.match(r"^\s*$", jean_bartik_application_user_id):
            self.assertEqual(jean_bartik_inst2, jean_bartik_inst1)
        else:
            self.fail("A valid application_user_id was not generated for User Jean Bartik")
