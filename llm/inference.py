
from transformers import pipeline
import threading


class LLM:
    def __init__(self):
        self.lock = threading.Lock()

        print("[LLM] Loading model...")
        self.generator = pipeline(
            "text-generation",
            model="distilgpt2"
        )
        print("[LLM] Model loaded")

    def _build_prompt(self, query, context):
        if context:
            return f"Context:\n{context}\n\nUser: {query}\nAI:"
        return f"User: {query}\nAI:"

    def generate(self, query, context=""):
        prompt = self._build_prompt(query, context)

        with self.lock:
            result = self.generator(
                prompt,
                max_length=120,
                temperature=0.7,
                num_return_sequences=1
            )

        text = result[0]["generated_text"]

        # remove prompt from output
        if text.startswith(prompt):
            text = text[len(prompt):]

        return text.strip()



_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = LLM()
    return _llm



def run_llm(query, context=""):
    llm = get_llm()
    return llm.generate(query, context)