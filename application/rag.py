from sentence_transformers import SentenceTransformer
import faiss
import httpx
import json
import numpy as np
import application.config as app_config
import os
import imghdr
import base64

class RAG:
    def __init__(self, docs, model_name="multi-qa-MiniLM-L6-cos-v1"):
        self.texts = [d["text"] for d in docs]
        self.urls = [d["url"] for d in docs]
        self.answers = [d["answer"] for d in docs]
        self.model = SentenceTransformer(model_name)
        if(len(docs)>0):
          self.embeds = self._embed_data()
          self.index = self._build_index()

    def _embed_data(self):
        return self.model.encode(self.texts, convert_to_numpy=True)

    def _build_index(self):
        dim = self.embeds.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(self.embeds)
        return index


    def retrieve(self, query, k=3):
        query_vec = self.model.encode([query], convert_to_numpy=True)
        D, I = self.index.search(np.array(query_vec), k)
        return [(self.texts[i], self.urls[i], self.answers[i]) for i in I[0]]
    

    def _detect_image_mime_type(self, image_base64: str) -> str:
        """Detect MIME type from base64-encoded image string."""
        try:
            image_data = base64.b64decode(image_base64)
            image_type = imghdr.what(None, h=image_data)
            if image_type:
                return f"image/{'jpeg' if image_type == 'jpg' else image_type}"
        except Exception:
            pass
        return "image/png"  # Fallback



    def generate_answer(self, question, instructions, image_base64=None):
        context_items = self.retrieve(question)
        context = "\n\n".join([f"{text} (Source: {url})" for text, url, answer in context_items])

        prompt = f"""{instructions}

Context:

{context}

Question: {question}
Answer:"""

        #print(f"Prompt:\n{prompt}")

        # 🔥 Use httpx to call OpenAI API
        headers = {
            "Authorization": f"Bearer {app_config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = None
        if image_base64:
            mime_type = self._detect_image_mime_type(image_base64)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        else:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]


        data = {
            "model": app_config.OPENAI_MODEL,
            "messages": messages,
            "temperature": 0.2
        }

        with httpx.Client(timeout=30) as client:
            response = client.post(app_config.OPENAI_API_URL, headers=headers, data=json.dumps(data))
            result = response.json()

        answer = result["choices"][0]["message"]["content"].strip()
        links = [{"url": url, "text": answer[:200] if answer else text[:200]} for text, url, answer in context_items]

        response = {"answer": answer, "links": links} 
        return response


    def save(self, path="rag_model"):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        np.save(f"{path}/embeds.npy", self.embeds)

        with open(f"{path}/metadata.json", "w") as f:
            json.dump({
                "texts": self.texts,
                "urls": self.urls,
                "answers": self.answers
            }, f)

    @classmethod
    def load(cls, path="rag_model", model_name="multi-qa-MiniLM-L6-cos-v1"):
        with open(f"{path}/metadata.json", "r") as f:
            metadata = json.load(f)

        instance = cls([], model_name=model_name)
        instance.texts = metadata["texts"]
        instance.urls = metadata["urls"]
        instance.answers = metadata["answers"]
        instance.model = SentenceTransformer(model_name)
        instance.embeds = np.load(f"{path}/embeds.npy")
        instance.index = faiss.read_index(f"{path}/index.faiss")
        return instance