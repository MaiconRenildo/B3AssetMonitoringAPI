from fastapi import FastAPI

app = FastAPI(
    docs_url="/",
    title="B3 Asset Monitoring API",
    description="B3 Asset Monitoring API",
    version="1.0.0"
)