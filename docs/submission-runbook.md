# Assessment submission runbook

This runbook is the final checklist for producing reviewable evidence. Run the
notebooks in a fresh environment, keep outputs visible, and commit only the
resulting artifacts. Fixture mode is for smoke tests and is not assessment
evidence.

## 1. Open the repository

1. Open `C:\Users\Admin\NSR\cdazz\finsight_ai` as the IDE workspace.
2. Confirm the Source Control panel shows this repository and branch `main`.
3. Run `git status` and confirm the expected modified and new files are listed.

## 2. Task 1

1. Open the Task 1 Colab badge in `task1_financial/README.md`.
2. Install `requirements-assessment.txt`.
3. Run every notebook cell with live mode enabled.
4. Keep the market table, indicator summary, sentiment results, report, and
   provenance outputs visible.
5. Commit the generated Markdown, HTML, chart, CSV, JSON, and metadata files
   under `task1_financial/artifacts/`.

## 3. Task 2

1. Open the Task 2 Colab badge in `task2_genai/README.md`.
2. Select a free T4 or L4 GPU runtime.
3. Store `GROQ_API_KEY` in Colab Secrets; never put it in the notebook.
4. Run the teacher health check and dataset generation cells.
5. Run QLoRA training and keep each epoch's train and validation loss visible.
6. Record any OOM attempt and the change that fixed it.
7. Run merged-model evaluation, complete ten manual labels, and select the RAG
   threshold using validation data only.
8. Commit dataset hashes, JSONL splits, configuration, losses, evaluation,
   manual review, model card, and the public model link.

## 4. Task 3

1. Open the Task 3 Colab badge in `task3_agentic/README.md`.
2. Run the single-agent graph and show a tool call, observation, and next
   action.
3. Run the two-agent graph and show the typed handoff, exactly one clarification
   request, and the incorporated answer.
4. Run the same request again and show `cached: true` without new tool calls.
5. Commit the real `logs/agent_trace.jsonl`, complete permitted tool outputs,
   reports, and cache files.

## 5. Final checks

1. Add the public GitHub URL, Colab URLs, and Task 2 model URL to the root
   README.
2. Open every link in a signed-out browser window.
3. Run the dependency-backed test suite and save the result.
4. Record the five-minute walkthrough using the companion PDF guide.
5. Review `CITATIONS.md` and `REFLECTION.md`, then commit and push the final
   revision.

Never claim live, teacher-generated, GPU-trained, or hosted results until the
corresponding cells have actually run and their outputs are present.
