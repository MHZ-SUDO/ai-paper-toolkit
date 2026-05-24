import os
from typing import Optional

from openai import OpenAI
from anthropic import Anthropic


class PaperGenerator:
    PROMPT_TEMPLATE = """You are an expert academic researcher. Write the following section of a research paper.

## Paper Title: {title}
## Section: {section}
## Citation Style: {citation_style}
## Research Context:
{context}

## Instructions:
1. Write in formal academic English with precise terminology
2. Include appropriate in-text citations where needed
3. Maintain logical flow and coherence
4. Be thorough but concise

## {section}:
"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        if "claude" in model.lower():
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        else:
            self.client = OpenAI(
                api_key=api_key or os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )

    def generate(
        self,
        title: str,
        sections: list[str],
        context: str,
        citation_style: str = "apa",
    ) -> dict[str, str]:
        results = {}
        for section in sections:
            prompt = self.PROMPT_TEMPLATE.format(
                title=title,
                section=section,
                citation_style=citation_style,
                context=context,
            )
            content = self._call_llm(prompt)
            results[section] = content
        return results

    def _call_llm(self, prompt: str) -> str:
        if isinstance(self.client, Anthropic):
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text
        else:
            resp = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content
