# imports

import os
from application.rag import RAG
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional


print("Imported required packages")

rag_model = RAG.load(path="rag_model")

print("Loaded RAG model")

app = FastAPI()


# Add CORS Middleware here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





class Link(BaseModel):
    url: str
    text: str


class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]


class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None 


instructions = '''
You are a helpful Teaching Assistant. Use the context below to help answer the question. If the context contains partial information, try to infer a helpful answer. Say "I don't know" only when no information related to the question is available in the context.
'''


@app.get("/")
def hello():
    return "Hello World !!!"

@app.post("/api", response_model=AnswerResponse)
def answer_question(request: QuestionRequest):
    question = request.question
    image = request.image  # base64 string or None
    print("==============================")
    print("question: ",question)
    if image:
        print("image: ",image)
    response = rag_model.generate_answer(question, instructions, image)
    print("RAG response: \n",response)
    return response