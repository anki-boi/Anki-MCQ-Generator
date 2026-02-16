from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_end_to_end_job_pipeline_and_exports() -> None:
    create_resp = client.post("/v1/jobs", json={"course_name": "Pharma", "output_format": ["csv"]})
    assert create_resp.status_code == 200
    job_id = create_resp.json()["job_id"]

    upload_resp = client.post(
        f"/v1/jobs/{job_id}/sources",
        data={"source_type": "text"},
        files={
            "file": (
                "notes.txt",
                "# Antibiotics\nPenicillin inhibits cell wall synthesis\n# Analgesics\nIbuprofen reduces inflammation\n",
                "text/plain",
            )
        },
    )
    assert upload_resp.status_code == 200

    start_resp = client.post(f"/v1/jobs/{job_id}/start")
    assert start_resp.status_code == 200

    status_resp = client.get(f"/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in {"parsing", "done", "chunking", "generating"}

    chunks_resp = client.get(f"/v1/jobs/{job_id}/chunks")
    assert chunks_resp.status_code == 200
    assert len(chunks_resp.json()["chunks"]) >= 1

    preview_resp = client.get(f"/v1/jobs/{job_id}/preview")
    assert preview_resp.status_code == 200
    body = preview_resp.json()
    assert body["status"] == "done"
    assert len(body["cards"]) >= 1
    assert body["validation"]["failed"] == 0

    csv_resp = client.get(f"/v1/jobs/{job_id}/export/csv")
    assert csv_resp.status_code == 200
    csv_body = csv_resp.json()
    assert csv_body["filename"].endswith(".csv")
    assert "|" in csv_body["content"]


def test_cannot_start_without_sources() -> None:
    create_resp = client.post("/v1/jobs", json={"course_name": "Biochem", "output_format": ["csv"]})
    job_id = create_resp.json()["job_id"]

    start_resp = client.post(f"/v1/jobs/{job_id}/start")
    assert start_resp.status_code == 400


def test_source_type_validation() -> None:
    create_resp = client.post("/v1/jobs", json={"course_name": "Biochem", "output_format": ["csv"]})
    job_id = create_resp.json()["job_id"]

    upload_resp = client.post(
        f"/v1/jobs/{job_id}/sources",
        data={"source_type": "video"},
        files={"file": ("notes.txt", "sample text", "text/plain")},
    )
    assert upload_resp.status_code == 422
