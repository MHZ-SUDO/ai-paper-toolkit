import json
from pathlib import Path
from typing import Optional

from openai import OpenAI
from anthropic import Anthropic


MODEL_CONFIGS = {
    "claude": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
    "deepseek": {"provider": "openai", "model": "deepseek-chat", "base_url": "https://api.deepseek.com"},
    "gpt": {"provider": "openai", "model": "gpt-4o"},
    "mimo": {"provider": "openai", "model": "mimo-v2-pro", "base_url": "https://platform.xiaomimimo.com/v1"},
}


class ModelComparator:
    def __init__(self, models: list[str]):
        self.models = models
        self.clients = {}
        for m in models:
            cfg = MODEL_CONFIGS.get(m, {})
            if cfg.get("provider") == "anthropic":
                self.clients[m] = Anthropic()
            else:
                self.clients[m] = OpenAI(base_url=cfg.get("base_url"))

    def evaluate(
        self,
        task: str,
        prompts: list[str],
        criteria: Optional[list[str]] = None,
    ) -> dict:
        results = {"task": task, "criteria": criteria or [], "models": {}}
        for model_name in self.models:
            scores = []
            for prompt in prompts:
                output = self._query_model(model_name, prompt)
                scores.append({"prompt": prompt[:100], "output_length": len(output)})
            results["models"][model_name] = scores
        return results

    def _query_model(self, model_name: str, prompt: str) -> str:
        cfg = MODEL_CONFIGS.get(model_name, {})
        client = self.clients[model_name]
        if isinstance(client, Anthropic):
            resp = client.messages.create(
                model=cfg.get("model", "claude-sonnet-4-20250514"),
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text
        else:
            resp = client.chat.completions.create(
                model=cfg.get("model", ""),
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content

    def report(self, results: dict, output: str = "report.md"):
        content = json.dumps(results, indent=2, ensure_ascii=False)
        Path(output).write_text(f"# Model Comparison Report\n\n```json\n{content}\n```", encoding="utf-8")
        print(f"Report saved to {output}")
