from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from datetime import datetime
import time
import json
import redis
import hashlib
from app.auth import get_current_user
from app.firebase import initialize_firebase

# Load environment variables
load_dotenv()

# Initialize Firebase
initialize_firebase()

# Initialize Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", ""),
    decode_responses=True,
)

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Initialize Pinecone vector store
vectorstore = PineconeVectorStore(
    index_name=os.getenv("PINECONE_INDEX_NAME"), embedding=embeddings
)

# Initialize Gemini
llm = GoogleGenerativeAI(model="gemini-2.0-flash")

# Create prompt template
prompt_template = """
You are an AI assistant named Bejo who helps answer questions about PT Bintang Toedjoe. Bejo has a personality that is joyful, friendly, informative, and insightful.

As Bejo, provide complete and informative answers in a natural and friendly language style. Bejo always responds in the same language that the user uses. If the user asks in Indonesian, Bejo answers in Indonesian. If the user asks in English, Bejo answers in English.

Context:
{context}

Question:
{question}

Answer (as Bejo with a joyful, friendly, informative, and insightful style):
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Create retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
)


# Generate a unique cache key based on the prompt
def generate_cache_key(prompt: str) -> str:
    return f"ai_query:{hashlib.md5(prompt.encode()).hexdigest()}"


# Cache TTL in seconds (1 day)
CACHE_TTL = 86400

# Router
router = APIRouter(prefix="/api", tags=["AI"])


class Query(BaseModel):
    prompt: str


@router.post("/asking")
async def process_query(query: Query, current_user=Depends(get_current_user)):
    try:
        # Start timing
        start_time = time.time()

        # Generate cache key
        cache_key = generate_cache_key(query.prompt)

        # Check if response is in cache
        cached_response = redis_client.get(cache_key)
        if cached_response:
            response = json.loads(cached_response)
            response["cache_hit"] = True
            response["latency"] = round(time.time() - start_time, 3)
            return response

        # Get similar documents from Pinecone
        similar_docs = vectorstore.similarity_search(query.prompt, k=4)

        # Combine context from similar documents
        context = "\n".join([doc.page_content for doc in similar_docs])

        # Get response from the chain
        result = qa_chain.invoke({"query": query.prompt})

        # Calculate latency
        end_time = time.time()
        latency = end_time - start_time

        # Calculate token usage
        prompt_tokens = llm.get_num_tokens(query.prompt)
        context_tokens = llm.get_num_tokens(context)
        response_tokens = llm.get_num_tokens(result["result"])

        # Format response
        response = {
            "response": result["result"],
            "token_used": {
                "prompt_tokens": prompt_tokens,
                "context_tokens": context_tokens,
                "response_tokens": response_tokens,
                "total_tokens": prompt_tokens + context_tokens + response_tokens,
            },
            "created_at": datetime.now().isoformat(),
            "latency": round(latency, 3),
            "cache_hit": False,
            "user": {"email": current_user["email"], "name": current_user["name"]},
        }

        # Cache the response
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(response))

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
