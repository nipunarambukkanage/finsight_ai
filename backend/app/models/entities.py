from datetime import datetime, timezone
import json
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="analyst")
    created_at = Column(DateTime, default=utcnow)

    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    market_cap = Column(Float, nullable=True)
    current_price = Column(Float, nullable=False)
    change_percent = Column(Float, default=0.0)
    pe_ratio = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    beta = Column(Float, default=1.0)
    week_52_high = Column(Float, nullable=True)
    week_52_low = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    price_history = relationship("PriceHistory", back_populates="stock", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    stock = relationship("Stock", back_populates="price_history")

class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False, default="My Watchlist")
    created_at = Column(DateTime, default=utcnow)

    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")
    user = relationship("User", back_populates="watchlists")

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    ticker = Column(String(10), nullable=False)
    added_at = Column(DateTime, default=utcnow)

    watchlist = relationship("Watchlist", back_populates="items")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False, default="Demo Institutional Portfolio")
    total_value = Column(Float, default=1000000.0)
    cash_balance = Column(Float, default=150000.0)
    created_at = Column(DateTime, default=utcnow)

    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    user = relationship("User", back_populates="portfolios")

class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    ticker = Column(String(10), nullable=False)
    shares = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    allocation_pct = Column(Float, default=0.0)

    portfolio = relationship("Portfolio", back_populates="holdings")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False)  # 10-K, 10-Q, Earnings, Research
    reporting_period = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="chunks")

class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    full_markdown = Column(Text, nullable=False)
    evidence_coverage = Column(Float, default=0.92)
    ai_confidence = Column(Float, default=0.88)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=utcnow)

class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=True, index=True)
    text = Column(Text, nullable=False)
    source = Column(String(100), default="analyst_news")
    label = Column(String(20), nullable=False)  # Positive, Neutral, Negative
    score = Column(Float, nullable=False)
    key_phrases = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

class MLExperiment(Base):
    __tablename__ = "ml_experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ticker = Column(String(10), nullable=False)
    task_type = Column(String(50), nullable=False)  # directional, volatility, regime
    model_type = Column(String(50), nullable=False)  # logistic_regression, random_forest, gradient_boosting
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    train_samples = Column(Integer, nullable=False)
    test_samples = Column(Integer, nullable=False)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    user_id = Column(String(100), default="demo_analyst")
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)
