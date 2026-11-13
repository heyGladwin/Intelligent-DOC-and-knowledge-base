import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

print("Indexes:", pc.list_indexes().names())

index = pc.Index(os.getenv("PINECONE_INDEX", "intelligent-doc"))
print(index.describe_index_stats())