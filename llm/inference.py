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

    def _buildPrompt(self, query, context):
        if context:
            return f"Context:\n{context}\n\nUser: {query}\nAI:"
        return f"User: {query}\nAI:"

    def generate(self, query, context=""):
        prompt = self._buildPrompt(query, context)

        with self.lock:
            result = self.generator(
                prompt,
                max_new_tokens=80,
                temperature=0.7,
                do_sample=True,
                num_return_sequences=1,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )

        text = result[0]["generated_text"]

        if text.startswith(prompt):
            text = text[len(prompt):]

        stopWords = ["User:", "AI:", "Context:"]
        for stopWord in stopWords:
            if stopWord in text:
                text = text.split(stopWord)[0]

        return text.strip()


_llm = None


def getLlm():
    global _llm
    if _llm is None:
        _llm = LLM()
    return _llm


def runLlm(query, context=""):
    llm = getLlm()
    return llm.generate(query, context)