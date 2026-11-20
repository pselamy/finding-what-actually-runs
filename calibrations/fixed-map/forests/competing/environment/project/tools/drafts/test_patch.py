import unittest

from patch import patch


class PatchTest(unittest.TestCase):
    def test_full_save(self):
        snapshot = {"title": "before", "body": "earlier"}
        update = {"title": "after", "body": "latest"}
        self.assertEqual(patch(snapshot, update), update)


if __name__ == "__main__":
    unittest.main()
