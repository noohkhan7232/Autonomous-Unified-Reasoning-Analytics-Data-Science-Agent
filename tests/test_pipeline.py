import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend import api


class WorkspaceTest(unittest.TestCase):
    def test_missing_numeric_feature_triggers_real_retraining(self):
        csv = "amount,label\n" + "".join(
            f"{index if index % 5 else ''},{int(index >= 30)}\n"
            for index in range(60)
        )
        with tempfile.TemporaryDirectory() as storage, patch.object(api, "ROOT", Path(storage)):
            with patch.dict("os.environ", {"GOOGLE_API_KEY": ""}), TestClient(api.app) as client:
                upload = client.post("/api/datasets/upload", headers={"X-Filename": "missing.csv"}, content=csv)
                self.assertEqual(upload.status_code, 201, upload.text)
                created = client.post("/api/analyses", json={"dataset_id": upload.json()["id"], "target": "label", "models": ["logistic_regression"]})
                self.assertEqual(created.status_code, 202, created.text)
                run_url = f'/api/analyses/{created.json()["id"]}'
                stream = client.get(run_url + "/events").text
                self.assertIn('"stage": "Self-correction", "status": "retrying"', stream)
                self.assertIn('"stage": "Self-correction", "status": "completed"', stream)
                run = client.get(run_url).json()
                self.assertEqual(run["status"], "completed")
                self.assertEqual(list(run["results"]["modeling"]["model_comparison"]), ["logistic_regression"])

    def test_csv_analysis_stream_and_persistence(self):
        csv = "amount,segment,label\n" + "".join(
            f"{index + group * 100},{'a' if group == 0 else 'b'},{group}\n"
            for group in range(2) for index in range(30)
        )
        with tempfile.TemporaryDirectory() as storage, patch.object(api, "ROOT", Path(storage)):
            with patch.dict("os.environ", {"GOOGLE_API_KEY": ""}), TestClient(api.app) as client:
                invalid = client.post("/api/datasets/upload", headers={"X-Filename": "wrong.txt"}, content=csv)
                self.assertEqual(invalid.status_code, 422)
                upload = client.post("/api/datasets/upload", headers={"X-Filename": "sample.csv"}, content=csv)
                self.assertEqual(upload.status_code, 201, upload.text)
                dataset = upload.json()
                self.assertEqual(dataset["rows"], 60)
                self.assertEqual([column["name"] for column in dataset["schema"]], ["amount", "segment", "label"])
                base = f'/api/datasets/{dataset["id"]}'
                self.assertEqual(client.get(base + "/profile").json()["duplicates"], 0)
                self.assertEqual(client.get(base + "/preview?search=b&limit=2").json()["total"], 30)
                payload = {"dataset_id": dataset["id"], "target": "missing"}
                self.assertEqual(client.post("/api/analyses", json=payload).status_code, 422)
                payload["target"] = "label"
                created = client.post("/api/analyses", json=payload)
                self.assertEqual(created.status_code, 202, created.text)
                run_id = created.json()["id"]
                run_url = f"/api/analyses/{run_id}"
                response = client.get(run_url + "/events")
                events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ") and line != "data: {}"]
                completed = {event["stage"] for event in events if event["status"] == "completed"}
                self.assertTrue({"Planning", "Modeling", "Evaluation", "Final report", "Execution"} <= completed, events)
                run = client.get(run_url).json()
                self.assertEqual(run["status"], "completed")
                self.assertEqual(len(run["results"]["modeling"]["model_comparison"]), 3)
                self.assertEqual(run["results"]["evaluation"]["verdict"], "PASS")
                self.assertEqual(run["results"]["explanation_status"], "unavailable")
                self.assertIn("System score", client.get(run_url + "/report").text)
                self.assertEqual(client.get(run_url + "/artifacts/target_distribution.png").status_code, 200)
                self.assertEqual(client.get(run_url + "/artifacts/workspace.sqlite3").status_code, 404)
            with TestClient(api.app) as reopened:
                self.assertEqual(reopened.get(run_url).json()["id"], run_id)
                self.assertEqual(reopened.delete(run_url).status_code, 204)
                self.assertEqual(reopened.get(run_url).status_code, 404)


if __name__ == "__main__":
    unittest.main()

