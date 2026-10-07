from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os

app = FastAPI()

ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET", "")
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """
    Tai file model.joblib tu cloud storage ve may khi server khoi dong.

    Ham nay duoc goi mot lan khi module duoc import. Su dung
    GOOGLE_APPLICATION_CREDENTIALS hoac AWS Credentials.
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # 1. Kiem tra va tai tu Google Cloud Storage neu co
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(ARTIFACT_BUCKET)
            blob = bucket.blob(MODEL_KEY)
            blob.download_to_filename(MODEL_PATH)
            print("Model da duoc tai xuong tu Google Cloud Storage.")
            return
        except Exception as e:
            print(f"Error downloading from GCS: {e}")

    # 2. Hoac tai tu AWS S3
    try:
        import boto3
        s3 = boto3.client("s3")
        s3.download_file(ARTIFACT_BUCKET, MODEL_KEY, MODEL_PATH)
        print("Model da duoc tai xuong tu AWS S3.")
        return
    except Exception as e:
        print(f"Notice/Error S3: {e}")

    # 3. Fallback cuc bo neu model da co san
    if os.path.exists("models/model.joblib") and not os.path.exists(MODEL_PATH):
        import shutil
        shutil.copy("models/model.joblib", MODEL_PATH)
        print("Model da duoc copy tu local path.")


download_model()
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.

    Tra ve: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung (khop voi thu tu trong FEATURE_NAMES cua test):
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    if len(req.features) != 10:
        raise HTTPException(
            status_code=400,
            detail="Expected 10 features (adult income)"
        )

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model is not loaded"
        )

    pred = int(model.predict([req.features])[0])
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"

    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
