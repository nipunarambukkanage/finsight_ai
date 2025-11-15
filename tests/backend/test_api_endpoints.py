import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_health_and_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "operational"
        assert data["demo_mode"] is True

@pytest.mark.asyncio
async def test_stocks_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List stocks
        res = await client.get("/api/v1/stocks/")
        assert res.status_code == 200
        stocks = res.json()
        assert len(stocks) >= 5
        tickers = [s["ticker"] for s in stocks]
        assert "AAPL" in tickers
        assert "MSFT" in tickers
        assert "NVDA" in tickers

        # Get single stock detail
        res_detail = await client.get("/api/v1/stocks/AAPL")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        assert detail["overview"]["ticker"] == "AAPL"
        assert "technicals" in detail
        assert "risk_stats" in detail
        assert "fundamentals" in detail

@pytest.mark.asyncio
async def test_portfolio_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/portfolio/")
        assert res.status_code == 200
        p = res.json()
        assert p["total_value"] > 0
        assert len(p["holdings"]) >= 3
        assert "sector_allocation" in p

@pytest.mark.asyncio
async def test_sentiment_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/sentiment/analyze", json={
            "text": "NVIDIA Blackwell chips see exponential demand surge across hyperscale cloud providers."
        })
        assert res.status_code == 200
        data = res.json()
        assert data["label"] == "Positive"
        assert data["score"] > 0.6

@pytest.mark.asyncio
async def test_showcase_capabilities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/showcase/capabilities")
        assert res.status_code == 200
        caps = res.json()
        assert len(caps) >= 10

        res_eval = await client.get("/api/v1/showcase/evaluation-benchmark")
        assert res_eval.status_code == 200
        eval_data = res_eval.json()
        assert "overall_metrics" in eval_data
