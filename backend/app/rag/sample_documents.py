"""
FinSight AI - Seed Sample Financial Documents
Legally safe, synthetic institutional-quality financial filings for demonstration:
- Apple Inc. Form 10-K Annual Report Summary (FY 2024)
- NVIDIA Corporation Q3 Fiscal 2025 Earnings Release & MD&A
- Microsoft Corporation Form 10-K Cloud & AI Business Overview (FY 2024)
"""

SAMPLE_FINANCIAL_DOCUMENTS = [
    {
        "ticker": "AAPL",
        "title": "Apple Inc. Form 10-K Annual Report (FY 2024)",
        "doc_type": "10-K",
        "reporting_period": "FY 2024",
        "year": 2024,
        "summary": "Full year 2024 annual report covering iPhone 16 rollout, Services segment gross margins reaching 74.2%, and geopolitical supply chain diversification.",
        "chunks": [
            {
                "page": 1,
                "content": "ITEM 1. BUSINESS OVERVIEW: Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services. Total net sales in fiscal 2024 reached $391.0 billion, up 2.0% year-over-year. Products net sales were $294.9 billion, while Services net sales achieved an all-time record of $96.2 billion, representing 24.6% of total revenue."
            },
            {
                "page": 4,
                "content": "SERVICES SEGMENT ANALYSIS: Services revenue grew 12.8% year-over-year to $96.17 billion. Gross margin for Services was 74.2%, compared to 70.8% in fiscal 2023, primarily driven by expanding paid subscriptions across Apple Music, iCloud, and the App Store. Total active installed base of devices surpassed 2.2 billion active devices globally."
            },
            {
                "page": 12,
                "content": "ITEM 1A. RISK FACTORS: Geopolitical and macroeconomic risks remain a primary consideration. The Company relies heavily on outsourced manufacturing and key component suppliers located in the Asia-Pacific region, particularly Taiwan, mainland China, and India. Any trade disputes, natural disasters, or export control regulations could materially disrupt production."
            },
            {
                "page": 18,
                "content": "REGULATORY & ANTITRUST SCRUTINY: The Company faces ongoing antitrust investigations and lawsuits globally regarding App Store distribution terms, commission structures (15% to 30%), and European Union Digital Markets Act (DMA) compliance requirements. Compliance mandates may reduce commission revenues and necessitate changes to iOS distribution architecture."
            }
        ]
    },
    {
        "ticker": "NVDA",
        "title": "NVIDIA Corporation Q3 Fiscal 2025 Earnings Release",
        "doc_type": "Earnings",
        "reporting_period": "Q3 FY2025",
        "year": 2025,
        "summary": "Q3 FY2025 financial release demonstrating record Data Center revenue of $30.8 billion powered by Hopper H100/H200 and initial Blackwell architecture shipments.",
        "chunks": [
            {
                "page": 1,
                "content": "EXECUTIVE SUMMARY: NVIDIA reported record revenue for the third quarter ended October 27, 2024, of $35.1 billion, up 17% from the previous quarter and up 94% from a year ago. Data Center revenue was $30.8 billion, up 112% from a year ago, driven by compute networking demand for hyperscale generative AI clusters."
            },
            {
                "page": 3,
                "content": "DATA CENTER & BLACKWELL PRODUCTION: Demand for Hopper architecture remains robust, while Blackwell AI superchips are in full production. Management noted that Blackwell demand is anticipated to exceed supply for several quarters in fiscal 2026 as Cloud Service Providers build out sovereign AI and frontier model infrastructure."
            },
            {
                "page": 6,
                "content": "FINANCIAL MARGINS & CASH FLOW: GAAP gross margin for the quarter was 74.6%, and non-GAAP gross margin was 75.0%. Operating income reached $21.87 billion, an increase of 110% year-over-year. Cash, cash equivalents and marketable securities stood at $38.5 billion, supporting ongoing share repurchases and R&D capital expenditure."
            },
            {
                "page": 9,
                "content": "RISKS & EXPORT RESTRICTIONS: The Company's Data Center business is subject to U.S. government export licensing requirements for advanced computing semiconductors shipped to China and certain Middle Eastern nations. Competition from custom ASICs (Google TPU, AWS Trainium, Microsoft Maia) remains a secondary monitorable factor."
            }
        ]
    },
    {
        "ticker": "MSFT",
        "title": "Microsoft Corporation Form 10-K Annual Report (FY 2024)",
        "doc_type": "10-K",
        "reporting_period": "FY 2024",
        "year": 2024,
        "summary": "Fiscal 2024 annual filing detailing Intelligent Cloud segment revenue of $105.4B, Azure revenue growth of 29%, and AI commercial infrastructure investments.",
        "chunks": [
            {
                "page": 2,
                "content": "CLOUD AND AI MOMENTUM: Fiscal 2024 revenue was $245.1 billion, increasing 16% year-over-year. Intelligent Cloud revenue surpassed $105.4 billion, growing 19%, propelled by Azure and other cloud services growth of 29%. More than 60,000 commercial customers now utilize Azure AI services."
            },
            {
                "page": 7,
                "content": "CAPITAL EXPENDITURES & PARTNERSHIPS: Capital expenditures including finance leases were $55.7 billion, supporting cloud and AI demand. The Company's strategic partnership with OpenAI continues to provide foundation models for Microsoft 365 Copilot, GitHub Copilot, and enterprise Azure OpenAI instances."
            },
            {
                "page": 14,
                "content": "RISK FACTORS - INFRASTRUCTURE & ENERGY: Escalating demand for AI training and inference requires significant datacenter capacity, high-bandwidth networking, and electrical power grid availability. Constraints in land, power access, or GPU hardware could restrain cloud expansion rate."
            }
        ]
    }
]
