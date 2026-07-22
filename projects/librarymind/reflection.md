# LibraryMind — Design Reflection

## Key Design Decisions

### Single AmaliProvider class for both OpenAI and Anthropic

The Amalitec proxy exposes a single base URL and routes requests to either OpenAI or
Anthropic based on a `Provider` request header. Rather than maintaining two separate
SDK clients, I implemented a single `AmaliProvider` class that accepts a `provider`
string (`"openai"` or `"anthropic"`) at construction time and injects the appropriate
header on every call. This keeps the retry logic, timeout configuration, and SSL
workaround (`verify=False`) in one place rather than duplicated across two classes.

The complication was that the proxy returns two different response shapes depending on
the provider: OpenAI-routed calls return `choices[0].message.content` while
Anthropic-routed calls return the native Anthropic format `content[0].text`. A single
`_extract_text()` method detects which shape is present and normalises to a plain
string before returning, so all callers receive a consistent interface regardless of
which provider was used.

The `ResilientAIService` wrapper sits above `AmaliProvider` and iterates through a
list of providers in order, catching exceptions and trying the next one. This gives
automatic fallback from OpenAI to Anthropic with no changes to the calling code.

### Local numpy bag-of-words embedding instead of the proxy

The original design called for the openai SDK pointed at the proxy to generate
embeddings. In practice, the proxy's `/embeddings` endpoint returns an empty
`200 OK` — it is a stub that was not yet implemented. After confirming this, I
looked at alternatives. ChromaDB ships its own default embedding function based on
an ONNX sentence transformer model, but it downloads the model weights from S3 on
first use — blocked by the corporate SSL proxy. The tiktoken library, which could
at least have provided accurate token counts, downloads its vocabulary from Azure
Blob Storage on first encoding call — also blocked.

What was available was `numpy`, installed as a transitive dependency of ChromaDB.
I implemented a deterministic bag-of-words embedding: each word is hashed with
SHA-256, the digest seeds a numpy random number generator, and a 1536-dimension
unit vector is drawn from it. A document's embedding is the sum of its word vectors,
L2-normalised to unit length. The same text always produces the same vector with no
network calls, no file downloads, and no external dependencies beyond numpy itself.

To compensate for weaker genre signal in bag-of-words, the seeded document text
repeats the genre label twice (`"Genre: Fantasy ... Genre: Fantasy"`), boosting its
weight in the sum and improving genre-based retrieval noticeably.

### RELEVANCE_THRESHOLD=0.05 instead of 0.7

Neural embedding models produce similarity scores typically in the 0.7–0.95 range
for semantically related content. Bag-of-words vectors, being sparse and
high-dimensional, produce much lower cosine similarities. After seeding the database
and running test queries, I measured that even the best matches scored only 0.06–0.31.
A threshold of 0.70 filtered every result. A threshold of 0.25 still eliminated
natural-language queries that scored around 0.09.

I settled on 0.05 — just above the effective noise floor for completely unrelated
content. This is the right threshold for the local model. When the proxy `/embeddings`
endpoint becomes available and real neural embeddings can be used, the threshold
should be raised to 0.25 or higher.

---

## Challenges

### SSL certificate interception blocking all external downloads

The corporate network intercepts HTTPS traffic using a custom CA certificate that is
not in the Windows system trust store. Every outbound HTTPS call from Python fails
with `CERTIFICATE_VERIFY_FAILED`. The workaround for the AI proxy calls was
`httpx.Client(verify=False)`. But this did not help with the package-level download
calls made inside ChromaDB and tiktoken — those libraries call `urllib` or `requests`
internally, and there was no public API to pass `verify=False` without patching the
libraries.

The solution was to not use those download-dependent features at all: local numpy
embedding replaced ChromaDB's ONNX model, and word-count estimation (`words * 4 // 3`)
replaced tiktoken for token counting.

### Anthropic proxy returning its own JSON format

When `Provider: anthropic` is sent, the proxy forwards the request to Anthropic and
returns the raw Anthropic API response — which is not in the OpenAI `choices[0]`
format. This caused silent failures where the response parsed without error but
`data["choices"]` raised a `KeyError`. Fixing it required inspecting live proxy
responses and writing the dual-format `_extract_text()` detection method described
above.

### Python 3.14 wheel incompatibility

The specified versions — `pydantic==2.8.0` and `tiktoken==0.7.0` — predate Python
3.14 and ship no `cp314` wheels. Pip attempts to compile them from source, which
requires a Rust toolchain for pydantic-core and a C compiler for tiktoken. Neither
was available in the environment. The fix was straightforward: bump to
`pydantic>=2.10.0`, `pydantic-settings>=2.4.0`, and `tiktoken>=0.13.0`, all of which
ship pre-built `cp314` wheels on PyPI.

---

## Debugging Story: The Embedding Discovery

The most instructive debugging sequence in the project started with a simple goal —
get the vector search working — and turned into a four-stage investigation.

**Stage 1:** I pointed the openai SDK at the proxy with a custom `base_url` and called
`client.embeddings.create()`. The response status was 401. The SDK was sending
`Authorization: Bearer <key>` but the proxy requires `X-Api-Key: <key>`. I switched
to a raw `httpx.post()` with the correct headers.

**Stage 2:** With correct auth, the `/embeddings` endpoint returned `200 OK` but the
body was `{}` — no `data` array, no vectors. The endpoint is a stub. I confirmed this
with multiple queries; all returned the same empty object.

**Stage 3:** I switched to ChromaDB's built-in `DefaultEmbeddingFunction`. On first
use it prints "downloading model weights" and makes an HTTPS call to an S3 bucket.
The call failed with `SSL: CERTIFICATE_VERIFY_FAILED`. I tried setting the
`REQUESTS_CA_BUNDLE` environment variable — the corporate CA was not available as a
file. I tried `pip install certifi` — the custom CA was not included there either.

**Stage 4:** I listed the packages available in the venv and noticed `numpy` was
present (a ChromaDB dependency). I designed the SHA-256 bag-of-words embedding on the
spot: hash each word into a seed, draw a unit vector, sum and normalise. The vectors
are deterministic, consistent, and need nothing beyond numpy. After seeding, the first
search returned plausible results — then I discovered the threshold needed tuning from
0.25 down to 0.05 by logging the actual similarity scores for known-good queries.

---

## What Works Well and What I Would Improve

**What works well:** All 10 lab scenarios pass end-to-end on the live system. The
two-provider resilience works correctly — if OpenAI fails, Anthropic handles the
request transparently. The chatbot maintains per-session history and produces coherent
multi-turn conversations. The classifier and summariser reliably return structured JSON
even when the LLM wraps its output in markdown fences. The FastAPI layer is thin,
stateless, and maps exceptions to the correct HTTP status codes consistently.

**What I would improve with more time:** The most important improvement would be
replacing the local embedding with real neural embeddings once the proxy `/embeddings`
endpoint is implemented — this would dramatically improve retrieval quality and allow
the relevance threshold to be raised to 0.25+, eliminating the off-topic false
positives. I would also add Redis caching (already wired; just needs a running
instance), persistent conversation storage (currently in-memory and lost on restart),
per-user rate limiting rather than global, and structured logging with a correlation ID
per request for easier debugging in production.
