from pinecone import Pinecone, ServerlessSpec
from utils import get_job_description_from_input
from sentence_transformers import SentenceTransformer
import pandas as pd
from transformers import pipeline
import torch
from dotenv import load_dotenv
import os

# Initialize Pinecone

load_dotenv()
pc = Pinecone(
        api_key=os.environ.get("PINECONE_API")
    )
index = pc.Index("shl-assessment-db")  

# Initialize model
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

if torch.cuda.is_available():
    model = model.to(torch.device("cuda"))

# Preprocess query to extract key job description
async def preprocess_query(user_query: str):
    processed_query = await get_job_description_from_input(user_query)
    return processed_query

async def query(user_query):
    preprocessed_query = await preprocess_query(user_query)
    query_embedding = model.encode([preprocessed_query], normalize_embeddings=True)

    # Query Pinecone
    results = index.query(
        vector=query_embedding[0].tolist(),  
        top_k=10,  
        include_metadata=True  
    )

    return results

async def get_assessments(user_query):
    results = await query(user_query)
    
    documents = [result['metadata']['document'] for result in results['matches']]
    metadatas = [result['metadata'] for result in results['matches']]
    distances = [result['score'] for result in results['matches']]
    
    sorted_results = sorted(zip(documents, metadatas, distances), key=lambda x: x[2], reverse=True)

    seen = set()
    recommendations = []
 
    for doc, metadata, distance in sorted_results:
        url = metadata.get("url", "N/A")
        remote_support = metadata.get('remote_testing', 'N/A')
        adaptive_support = metadata.get('adaptive', 'N/A')
        duration = str(metadata.get('duration', 'N/A'))
        test_type = metadata.get('test_types', 'N/A')
        description = metadata.get('description', 'N/A')
        
        if url in seen:
            continue
        else:
            seen.add(url)
            recommendations.append({
                'url': url,
                'adaptive_support': adaptive_support,
                'description': description,
                'duration': duration,
                'remote_support': remote_support,
                'test_type': test_type
            })
        
    return recommendations
