from todo.test_base import BaseTestCase

import unittest
from flask import json, url_for

class IndexTestCase(BaseTestCase):

    def test_index(self):
        response = self.app.get(url_for("index"))
        self.assertEqual(response.status_code, 200)

    def test_cors_headers(self):
        response = self.app.get(url_for("index"), headers={"Origin": "www.example.com"})
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "www.example.com")

    def test_index_allows_posts(self):
        data = dict(title="some text")
        response = self.app.post(url_for("index"),
                data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_index_returns_lists(self):
        response = self.app.get(url_for("index") )
        self.assertIsInstance(json.loads(response.data.decode("utf-8")), list)

    def test_index_returns_entry(self):
        data = dict(title="some other text")
        response = self.app.post(url_for("index"),
                data=json.dumps(data), content_type="application/json")
        self.assertEqual(data["title"], json.loads(response.data)["title"])

    def test_index_allows_delete(self):
        response = self.app.delete(url_for("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_responds_with_empty_array_after_delete(self):
        response = self.app.delete(url_for("index"))
        self.assertEqual(response.data.decode("utf-8"), "[]")

    def test_index_saves_posted_data(self):
        data = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data), content_type="application/json")
        response = self.app.get(url_for("index"))
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response_data[0]["title"], data["title"])

    def test_index_deletes_all_entries_after_delete(self):
        data1 = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data1), content_type="application/json")
        data2 = dict(title="some different text")
        self.app.post(url_for("index"), data=json.dumps(data2), content_type="application/json")
        data3 = dict(title="more different text")
        self.app.post(url_for("index"), data=json.dumps(data3), content_type="application/json")
        self.app.delete(url_for("index"))
        response = self.app.get(url_for("index"))
        self.assertEqual(response.data.decode("utf-8"), "[]")

    def test_index_returns_multiple_entries_properly_formatted(self):
        data1 = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data1), content_type="application/json")
        data2 = dict(title="some different text")
        self.app.post(url_for("index"), data=json.dumps(data2), content_type="application/json")
        data3 = dict(title="more different text")
        self.app.post(url_for("index"), data=json.dumps(data3), content_type="application/json")
        response = self.app.get(url_for("index"))
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response_data[0]["title"], data1["title"])
        self.assertEqual(response_data[1]["title"], data2["title"])
        self.assertEqual(response_data[2]["title"], data3["title"])

    def test_index_returns_no_comma_at_the_end_of_the_list(self):
        data = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data), content_type="application/json")
        response = self.app.get(url_for("index"))
        self.assertEqual(response.data.decode("utf-8")[-2:], "}]")

    def test_entries_contain_completed_property(self):
        data = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data), content_type="application/json")
        response = self.app.get(url_for("index"))
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("completed", response_data[0])

    def test_new_entries_have_completed_property(self):
        data = dict(title="different text")
        response = self.app.post(url_for("index"),
                data=json.dumps(data), content_type="application/json")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("completed", response_data)

    def test_new_entries_are_not_completed_post(self):
        data = dict(title="different text")
        response = self.app.post(url_for("index"),
                data=json.dumps(data), content_type="application/json")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response_data["completed"], False)

    def test_new_entries_are_not_completed_get(self):
        data = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data), content_type="application/json")
        response = self.app.get(url_for("index"))
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response_data[0]["completed"], False)

    def test_new_entries_have_url_property(self):
        data = dict(title="different text")
        response = self.app.post(url_for("index"),
                data=json.dumps(data), content_type="application/json")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("url", response_data)

    def test_entries_have_url_property(self):
        data = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data), content_type="application/json")
        response = self.app.get(url_for("index"))
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("url", response_data[0])

    def test_entries_have_proper_url(self):
        data = dict(title="different text")
        self.app.post(url_for("index"), data=json.dumps(data), content_type="application/json")
        response = self.app.get(url_for("index"))
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(url_for("entry", entry_id=1, _external=True), response_data[0]["url"])

    def test_new_entries_have_proper_url(self):
        data = dict(title="different text")
        response = self.app.post(url_for("index"),
                data=json.dumps(data), content_type="application/json")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(url_for("entry", entry_id=1, _external=True), response_data["url"])

class EntryTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.data = dict(title="text")
        self.app.post(url_for("index"),
                data=json.dumps(self.data), content_type="application/json")

    def test_entry_returns_entry(self):
        response = self.app.get(url_for("entry", entry_id=1))
        self.assertEqual(response.status_code, 200)

    def test_entry_returns_correct_entry(self):
        response = self.app.get(url_for("entry", entry_id=1))
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(self.data["title"], response_data["title"])

if __name__ == "__main__":
    unittest.main()
