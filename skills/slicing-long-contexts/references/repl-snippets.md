# REPL Snippets for RLM CLI Runner

Minimal Python helpers to run in the REPL when the long prompt is stored as `prompt`.

## Peeking / stats
```python
len(prompt)
prompt[:500]          # first 500 chars
prompt[-500:]         # tail
prompt.count("Chapter")
```

## Finding boundaries
```python
import re
# first occurrence of a marker
i = prompt.find("Chapter 2")
# all chapter headers
chapters = [m.start() for m in re.finditer(r"Chapter \d+", prompt)]
```

## Chunking by markers
```python
def slice_between(text, start_pat, end_pat=None):
    import re
    s = re.search(start_pat, text)
    if not s:
        return ""
    start = s.start()
    if end_pat:
        e = re.search(end_pat, text[s.end():])
        end = s.end() + e.start() if e else len(text)
    else:
        end = len(text)
    return text[start:end]

chapter1 = slice_between(prompt, r"Chapter 1", r"Chapter 2")
```

## Fixed-size chunking
```python
chunk_size = 4000
chunks = [prompt[i:i+chunk_size] for i in range(0, len(prompt), chunk_size)]
```

## Batching guidance (avoid too many sub-calls)
```python
target = 200_000  # chars per sub-call to reduce count
chunks = [prompt[i:i+target] for i in range(0, len(prompt), target)]
```

## Keyword filtering
```python
# Grab lines with a keyword
lines = [ln for ln in prompt.splitlines() if "ring" in ln.lower()]
```

## Writing slices to temp files for CLI sub-calls
```python
from pathlib import Path
Path('/tmp/rlm_slice.txt').write_text(chapter1)
```

## Aggregating sub-responses
```python
resp1 = "The silver flask..."
resp2 = "Herod's ring..."
final = f"From chapter 1: {resp1}\nFrom chapter 3: {resp2}"
print(final)
```

## Wrap sub-call helper (simulating llm_query)
```python
import subprocess, tempfile, textwrap
def llm_query(text, instruction, model="gpt-4o"):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(text.encode())
        slice_path = f.name
    cmd = ["codex", "--model", model, textwrap.dedent(f"{instruction}\n---\n$(cat {slice_path})")]
    # Note: if using gemini, swap binary/flags accordingly.
    out = subprocess.check_output(" ".join(cmd), shell=True, text=True)
    return out
```

## Dynamic context + logging (shell)
```bash
# inspect long outputs without pasting
tail -n 40 /tmp/rlm_subresp_ch1.txt
rg "flask" /tmp/rlm_subresp_ch1.txt

# append a structured log outside the skill dir
echo '{"step":"subcall_ch1","status":"ok","slice":"/tmp/rlm_slice_ch1.txt"}' >> progress.log

# keep final answer as a file/variable (analogue to FINAL_VAR)
cat /tmp/rlm_final.txt
```
