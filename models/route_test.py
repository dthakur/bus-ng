import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from route import Route

class RouteTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

        # Create a consistency policy that will simulate the High Replication consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_entity(self):
        Route(tag="1", title = "1").put()
        self.assertEqual(1, len(Route.query().fetch()))

    def test_put_then_get_by_key(self):
        key = Route(tag="1", title = "1").put()
        key.get()

    def test_put_then_get_query(self):
        key = Route(tag="1", title = "1").put()
        entities = Route.query(Route.tag == "1").fetch()
        self.assertEqual(1, len(entities))

    def test_determinisitic_outcome(self):
        self.policy.SetProbability(.5)  # 50% chance to apply.
        self.policy.SetSeed(2) # Use the pseudo random sequence derived from seed=2.

        Route(tag="1", title = "1").put()

        self.assertEqual(0, Route.query().count(3))
        self.assertEqual(0, Route.query().count(3))

        # Will always be applied before the third query.
        self.assertEqual(1, Route.query().count(3))
        self.policy.SetProbability(0)

if __name__ == '__main__':
    unittest.main()
