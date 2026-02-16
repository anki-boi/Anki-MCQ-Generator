from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_end_to_end_job_pipeline_and_exports() -> None:
    create_resp = client.post("/v1/jobs", json={"course_name": "Pharma", "output_format": ["csv", "apkg"]})
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

    chunks_resp = client.get(f"/v1/jobs/{job_id}/chunks")
    assert chunks_resp.status_code == 200
    assert len(chunks_resp.json()["chunks"]) >= 1

    preview_resp = client.get(f"/v1/jobs/{job_id}/preview")
    assert preview_resp.status_code == 200
    preview_body = preview_resp.json()
    assert preview_body["validation"]["total"] >= 1
    assert preview_body["validation"]["passed"] >= 1

    validation_resp = client.get(f"/v1/jobs/{job_id}/validation")
    assert validation_resp.status_code == 200
    validation_body = validation_resp.json()
    assert "summary" in validation_body
    assert "failed_cards" in validation_body

    export_csv_resp = client.post(f"/v1/jobs/{job_id}/export", json={"format": "csv"})
    assert export_csv_resp.status_code == 200
    export_csv_id = export_csv_resp.json()["export_id"]

    download_csv_resp = client.get(f"/v1/exports/{export_csv_id}/download")
    assert download_csv_resp.status_code == 200
    csv_payload = download_csv_resp.json()
    assert csv_payload["filename"].endswith(".csv")
    assert csv_payload["content_type"] == "text/csv"
    assert "|" in csv_payload["content"]

    export_apkg_resp = client.post(f"/v1/jobs/{job_id}/export", json={"format": "apkg"})
    assert export_apkg_resp.status_code == 200
    export_apkg_id = export_apkg_resp.json()["export_id"]

    download_apkg_resp = client.get(f"/v1/exports/{export_apkg_id}/download")
    assert download_apkg_resp.status_code == 200
    apkg_payload = download_apkg_resp.json()
    assert apkg_payload["filename"].endswith(".apkg")
    assert "DECK=" in apkg_payload["content"]


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


def test_download_missing_export() -> None:
    missing_resp = client.get("/v1/exports/exp_unknown/download")
    assert missing_resp.status_code == 404
