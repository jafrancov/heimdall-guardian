# Local AI

The AI review is optional and **can take several minutes**. It only runs in the `full` and
`vendor` profiles, or in a custom one that includes the AI module, and it uses a model that
runs **on your machine or on your network**: never a cloud service. The simplest way is
[Ollama](https://ollama.com).

## Set it up

1. Install Ollama from [ollama.com/download](https://ollama.com/download) and leave it
   open. It listens on `http://localhost:11434`.
2. Download a model and check its exact name:

    ```bash
    ollama pull qwen2.5-coder:14b
    ollama list
    ```

3. Register it in **Settings → AI review**, or in `config.toml`:

    ```toml
    [llm]
    enabled = true
    active_destination = "laptop"

    [[llm.destinations]]
    name = "laptop"
    runtime = "ollama"
    url = "http://localhost:11434/v1"
    model_triage = "qwen2.5-coder:14b"       # assesses whether a serious finding is real
    model_endpoints = "qwen2.5-coder:14b"    # reviews the access control of each endpoint
    model_summary = "qwen2.5-coder:14b"      # writes the executive summary
    model_sinks = "<unset>"                  # optional: reviews risky operations; defaults to model_triage
    model_consensus = "<unset>"              # optional: a second model to cross-check
    ```

4. Check it:

    ```bash
    uv run hdl llm
    ```

[LM Studio](https://lmstudio.ai) (`http://localhost:1234/v1`) and your own vLLM server also
work. You can register several destinations (each a `[[llm.destinations]]` block) and pick
one per analysis with `hdl scan <folder> --profile full --ai <name>`.

## Which model

- To assess findings and endpoints, a code-oriented *instruct* model (`coder` or `code` in
  the name).
- For the summary, any general model with good language skills: it only receives figures,
  never code.
- A model of 7 to 8 billion parameters needs about 8 GB of free memory; one of 14, about
  12 GB; one of 30 or more, 24 GB and up.
- A second, different model in `model_consensus` makes two models assess each finding. It
  takes twice as long.
- Not suitable: embedding models and those ending in `:cloud`.

## Reasoning models

Some models (for example the "thinking" builds of Qwen) spend hundreds of tokens on hidden
reasoning before answering. With the short replies Heimdall asks for, the JSON can be cut off
or come back empty, and the answer counts as unusable. By default Heimdall asks the runtime
not to reason (`reasoning = "off"` in the destination, sent as `reasoning_effort: "none"`);
if the runtime rejects that field, it is dropped and not tried again. Set `reasoning = "on"`
(or tick "Let the model reason before answering" in Settings) to let it think first: answers
may be better, but each query is much slower. When most replies are unusable, the run says so
in its limitations.

## Privacy (principle P3)

The destination must be `localhost`, `127.0.0.1` or `::1`, or satisfy the destination rules:
the host is in `allowed_hosts`, or it is a private IP or internal domain, and it uses HTTPS.
Models with the `:cloud` suffix and cloud AI command-line tools are rejected.

Code is sent to the model without comments and with secrets masked.

## What the AI does and does not do

- **Risky operations (T4).** Candidate rules mark operations that are dangerous when user
  input reaches them (a query built from a string, a command, a file path, unsafe
  deserialization, XML parsed with external entities). It covers PHP, Python, JavaScript,
  C#, Kotlin, Swift and Dart code. The AI checks,
  with the whole function and up to two of its callers, whether user input really reaches
  them. Only a high risk with "reachable: yes" becomes an AI finding, always MEDIUM, that
  does not count for the verdict until a person confirms it. This is where the AI finds
  problems the rules alone do not report.
- **Endpoints (T2).** It reviews the access control of each endpoint with the code that
  decides it: the real handler (found from the route), the route declaration with its
  middleware and up to three project functions the handler calls. If the handler is not
  found, the review is kept but no suggestion is created.
- **Serious findings (T1).** It assesses critical and high findings, but only those whose
  rule does not already have high confidence.
- **Summary (T3).** It writes the executive summary from aggregate figures, never code.
- The run budget is shared in this order: T4 (up to 60 %), then T2, then T1. The total time
  is the same as before, but it is spent where it finds new problems.
- `model_sinks` sets the model for T4 per destination; if unset, `model_triage` is used.
- It never walks the whole repository.
- It does not change a finding's severity or status, even if it thinks it is a false
  positive: its results always appear marked as a suggestion.
- AI suggestions do not count toward the vendor verdict unless a human confirms them.
- Answers are cached, so repeating an unchanged analysis is almost instant.
