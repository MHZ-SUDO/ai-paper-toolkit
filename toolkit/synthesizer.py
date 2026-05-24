from openai import OpenAI


SYNTHESIS_PROMPT = """You are a research assistant helping with a literature review.

## Research Topic: {topic}
## Papers to Synthesize:
{papers}

## Instructions:
1. Identify common themes across papers
2. Highlight conflicting findings or methodological differences
3. Identify research gaps
4. Suggest future research directions
5. Include brief citations to the source papers

## Synthesis:
"""


class LiteratureSynthesizer:
    def __init__(self, api_key: str = None, model: str = "gpt-4o", base_url: str = None):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def synthesize(self, topic: str, papers: list[dict]) -> str:
        papers_text = "\n\n".join(
            f"Paper {i+1}: {p.get('title', 'Untitled')}\n{p.get('abstract', 'No abstract')}"
            for i, p in enumerate(papers)
        )
        prompt = SYNTHESIS_PROMPT.format(topic=topic, papers=papers_text)
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    def find_gaps(self, topic: str, existing_papers: list[dict]) -> str:
        papers_summary = "\n".join(
            f"- {p['title']}: {p.get('abstract', '')[:200]}..."
            for p in existing_papers
        )
        prompt = f"""Based on these existing papers on "{topic}", identify specific research gaps:

{papers_summary}

List 3-5 concrete, actionable research gaps with brief justification."""
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
