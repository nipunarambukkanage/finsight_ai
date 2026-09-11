# FinSight AI citations

This repository was developed with AI assistance and documents the required provenance for the assessment.

## AI-assisted code

- `# AI-ASSISTED: OpenAI Codex (GPT-6), Prompt: 'Implement the FinSight AI assessment and industrial platform plan with typed financial pipelines, QLoRA training, and agent workflows', Date: 2026-09-11`
- `# AI-ASSISTED: OpenAI Codex (GPT-6), Prompt: 'Review repository architecture and identify correctness, security, persistence, and assessment gaps', Date: 2026-09-11`

The assistant produced initial implementation drafts; the repository owner is responsible for reviewing, testing, and defending every change.

## External documentation and libraries

- yfinance API: https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- Hugging Face PEFT quantization/QLoRA: https://huggingface.co/docs/peft/developer_guides/quantization
- Qwen2.5-1.5B-Instruct model card: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
- Groq models and rate limits: https://console.groq.com/docs/models and https://console.groq.com/docs/rate-limits
- DDGS package migration discussion: https://github.com/deedy5/ddgs/discussions/418
- Langfuse self-hosting: https://langfuse.com/self-hosting

## Teacher-model prompt

The complete Task 2 teacher prompt is versioned in `task2_genai/src/prompts.py` and copied into the dataset metadata produced by the notebook. Teacher outputs must be validated and retained with their model name, revision, and generation settings.

