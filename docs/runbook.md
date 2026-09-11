# Local runbook

Core demo services:

```bash
docker compose up --build
```

Optional durable events and AI observability profiles:

```bash
docker compose -f docker-compose.yml -f docker-compose.integrations.yml --profile events --profile observability up
```

Run the assessment paths without Docker:

```bash
pip install -r requirements-assessment.txt
pip install -e ".[assessment,test]"
python task1_financial/run_pipeline.py --ticker AAPL --demo
python task3_agentic/run_agent.py --ticker AAPL --two-agent
python task3_agentic/run_agent.py --ticker AAPL --two-agent --demo  # explicit offline fixture mode
```

Use `requirements-training.txt` in a fresh Colab GPU session for Task 2.
Provider keys belong in an untracked `.env` or the Colab secret store. Never
place tokens in notebooks, JSONL traces, model artifacts, or Git history.

Before submitting the assessment, execute each notebook and commit only the
resulting reproducible artifacts. Regenerate the Task 3 trace, complete the
ten-output manual review for Task 2, publish the merged model when training
succeeds, and verify repository/model/Drive links in a signed-out browser.
Record a personally narrated walkthrough of no more than five minutes; the
video is mandatory even when only one assessment task is submitted.
