from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
import pandas as pd


df = pd.read_excel(r"D:\SHL ASSESSMENT\summarized_assessment_data_with_desc_new.xlsx")

df["combined"] = (
    "Represent this document for retrieval: " +
    "Name: " + df["Name"] + "\n" +
    "Summary: " + df["summarized_description"] + "\n" +
    "Duration: " + df["Duration"].astype(str) + "\n" +
    "Job Levels: " + df["Job Levels"]
)

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

embeddings = model.encode(df["combined"].tolist(), 
                          batch_size=32,
                          show_progress_bar=True, 
                          normalize_embeddings=True)


load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API"))

index_name = "shl-assessment-db"
if index_name in pc.list_indexes():
    pc.delete_index(index_name)

pc.create_index(
    name=index_name,
    dimension=1024,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

index = pc.Index(index_name)

vectors = [(f"id_{i}", embeddings[i], {
        "document": df["combined"][i],
        "name": df["Name"][i],
        "duration": str(df["Duration"][i]),
        "job_levels": df["Job Levels"][i],
        "url": df["URL"][i],
        "description": df["Description"][i],
        "adaptive": str(df["Adaptive/IRT"][i]),
        "remote_testing": str(df["Remote Testing"][i]),
        "test_types": df["Test Types"][i]
    })
    for i in range(len(df))
]

index.upsert(vectors)