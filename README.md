=> Full Stack Development Assignment

=> Part 1 - Token/Cost Optimization

The problem: an agent pipeline was using around 100K input tokens per query, which gets expensive and slow at scale.

I implemented two optimizations in `token_optimization_demo.py`.

-> RAG (retrieval-augmented generation)** - instead of sending the entire reference document into the prompt every time, I chunk the document and only send the part relevant to the query. In the demo this uses a simple keyword match, but in a real system this would use embeddings (e.g. Gemini or OpenAI embeddings) stored in a vector database like MongoDB Atlas Vector Search, so it can match on meaning and not just exact words. In my test this cut tokens from about 1367 to 72, roughly a 95% reduction.

-
-> 90% reduction. In the demo the summary is hardcoded since I don't have API access set up here, but normally this would come from a small/cheap LLM call.

Tradeoff: if the RAG retrieval grabs the wrong chunk, or the summary drops something important, output quality can suffer a bit. Using proper embeddings instead of keyword matching helps reduce this risk.

Run it with:
```
python token_optimization_demo.py
```

Part 2 - Debugging

The problem: a multi-step agent pipeline that sometimes times out, sometimes returns malformed output, and sometimes silently succeeds with wrong data.

My first move is always adding per-step logging (input/output of every agent step), because otherwise I'm just guessing where the problem is.

For timeouts, I check per-step timing to find which step is slow, and look at retry/backoff config and rate limits.

For malformed output, I check the raw LLM response before parsing to see what actually came back, and review whether the prompt clearly specifies the expected format.

For silent wrong data - the hardest one, since there's no error - I build a small golden dataset (10-15 questions with known correct answers), run the pipeline against it, and for any mismatches I trace that specific case's retrieval step and reasoning step to find where it went wrong.

Part 3 - CI/CD and Deployment

`.github/workflows/ci-cd.yml` has two jobs.

`test-and-lint` runs on every push - installs deps, runs flake8 and pytest.

`deploy-staging` only runs on merges to main, and only after test-and-lint passes (`needs: test-and-lint`), so broken code can't get deployed.

Secrets (API keys etc) are never hardcoded - they're stored in GitHub Secrets (Settings > Secrets and variables > Actions) and injected at runtime via `${{ secrets.STAGING_API_KEY }}`. GitHub also masks secret values in logs automatically.

Rollback plan if a deploy breaks production: first move is reverting to the last stable version immediately (`git revert` + redeploy, or a one-click rollback if the platform supports it) - fixing the root cause comes after, since the priority is stopping user impact. After that I check monitoring to confirm things are back to normal, then dig into what actually went wrong.

Structure
```
.github/workflows/ci-cd.yml
token_optimization_demo.py
tests/test_sample.py
requirements.txt
README.md
```
