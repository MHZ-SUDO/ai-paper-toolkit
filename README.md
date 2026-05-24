# AI Paper Toolkit

AI-assisted academic paper writing and LLM evaluation toolkit.

## Features

- **Paper Draft Generator**: Generate structured paper drafts from research outlines using LLMs
- **Model Comparison Runner**: Batch-test multiple LLMs on academic writing tasks with standardized prompts
- **Literature Synthesizer**: Cross-reference and synthesize findings from multiple papers
- **Benchmark Evaluator**: Evaluate LLM performance on domain-specific academic tasks

## Supported Models

| Model | API Format | Status |
|-------|-----------|--------|
| Claude (Anthropic) | REST API | Tested |
| DeepSeek | OpenAI-compatible | Tested |
| GPT (OpenAI) | OpenAI-compatible | Tested |
| MiMo (Xiaomi) | OpenAI-compatible | In Progress |

## Quick Start

```bash
pip install -r requirements.txt
```

### Generate a paper draft

```python
from toolkit import PaperGenerator

generator = PaperGenerator(api_key="your-key", model="claude-sonnet-4-20250514")
draft = generator.generate(
    title="Your Research Title",
    sections=["abstract", "introduction", "methods", "results", "discussion"],
    context="Your research methodology and key findings...",
    citation_style="apa"
)
```

### Run model comparison

```python
from toolkit import ModelComparator

comparator = ModelComparator(models=["claude", "deepseek", "gpt"])
results = comparator.evaluate(
    task="abstract_generation",
    prompts=test_prompts,
    criteria=["coherence", "accuracy", "conciseness"]
)
comparator.report(results, output="comparison_report.md")
```

## Project Structure

```
ai-paper-toolkit/
├── README.md
├── requirements.txt
├── toolkit/
│   ├── __init__.py
│   ├── paper_generator.py    # LLM-based paper draft generation
│   ├── comparator.py          # Multi-model benchmark runner
│   └── synthesizer.py         # Literature cross-reference tool
└── prompts/
    └── academic_prompts.json  # Domain-specific prompt templates
```

## License

MIT
