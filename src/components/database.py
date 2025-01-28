# Import the Pinecone library
from pinecone import Pinecone, ServerlessSpec
import time
import yaml
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
from dotenv import load_dotenv,find_dotenv
import pandas as pd
import ast
from sentence_transformers import SentenceTransformer

load_dotenv(find_dotenv())

# Extract the PINECONE_API_KEY from the configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
# Extract the PINECONE_INDEX_NAME from the configuration
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
# Extract the PINECONE_DIMENSION from the configuration
PINECONE_DIMENSION = 768
# Extract the PINECONE_METRIC from the configuration
PINECONE_METRIC = os.getenv('PINECONE_METRIC')
# Extract the PINECONE_CLOUD from the configuration
PINECONE_CLOUD = os.getenv('PINECONE_CLOUD')
# Extract the PINECONE_REGION from the configuration
PINECONE_REGION = os.getenv('PINECONE_REGION')


# Create a Pinecone instance
pinecone = Pinecone(api_key=PINECONE_API_KEY)

def create_index():
    try:
        # Check if index exists
        if PINECONE_INDEX_NAME not in pinecone.list_indexes().names():
            pinecone.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=PINECONE_DIMENSION,
                metric=PINECONE_METRIC,
                spec=ServerlessSpec(
                    cloud='aws',  # You can specify the cloud provider here, e.g., aws or gcp
                    region=PINECONE_REGION
                )
            )
            print(f"Index '{PINECONE_INDEX_NAME}' created successfully.")
        else:
            print(f"Index '{PINECONE_INDEX_NAME}' already exists.")
    except Exception as e:
        print(f"Error creating index: {e}")

# Delete a Pinecone index
def delete_index():
    try:
        # Delete a Pinecone index
        pinecone.delete_index(name=PINECONE_INDEX_NAME)
        print(f'Index {PINECONE_INDEX_NAME} deleted successfully')
    except Exception as e:
        print(f'Error deleting index {PINECONE_INDEX_NAME}: {e}')

# List all Pinecone indexes
def list_indexes():
    try:
        # List all Pinecone indexes
        indexes = pinecone.list_indexes()
        print(f'Indexes: {indexes}')
    except Exception as e:
        print(f'Error listing indexes: {e}')

# Get a Pinecone index
def get_index():
    try:
        # Get a Pinecone index
        index = pinecone.get_index(name=PINECONE_INDEX_NAME)
        print(f'Index: {index}')
    except Exception as e:
        print(f'Error getting index {PINECONE_INDEX_NAME}: {e}')

# Insert a single item into a Pinecone index
def insert_items(path):
    try:
        # Connect to the Pinecone index
        index = pinecone.Index(PINECONE_INDEX_NAME)

        # Load data from Excel file
        data = pd.read_excel(path)
        sentences = data["Name of medicine"].astype(str).tolist()

        # Generate embeddings using SentenceTransformer
        model = SentenceTransformer("thenlper/gte-base")
        embeddings = model.encode(sentences)

        # Split the embeddings into smaller chunks
        chunk_size = 100  # Define chunk size based on your limit (e.g., 100 items at a time)
        for i in range(0, len(embeddings), chunk_size):
            vectors = [{"id": str(idx + i), "values": embedding.tolist()} for idx, embedding in enumerate(embeddings[i:i + chunk_size])]
            index.upsert(vectors)
            print(f"Inserted {len(vectors)} items into the index '{PINECONE_INDEX_NAME}'.")

    except Exception as e:
        print(f"Error inserting items: {e}")

# Delete a single item from a Pinecone index
def delete_item(item_id):
    try:
        # Delete the item from the Pinecone index
        pinecone.delete(index_name=PINECONE_INDEX_NAME, ids=[item_id])
        print(f'Deleted item {item_id} from index {PINECONE_INDEX_NAME}')
    except Exception as e:
        print(f'Error deleting item {item_id} from index {PINECONE_INDEX_NAME}: {e}')

# Search for similar items in a Pinecone index
def search_items(item_id):
    try:
        # Search for similar items in the Pinecone index
        results = pinecone.query(index_name=PINECONE_INDEX_NAME, ids=[item_id], top_k=5)
        print(f'Similar items to item {item_id}: {results}')
    except Exception as e:
        print(f'Error searching for similar items to item {item_id} in index {PINECONE_INDEX_NAME}: {e}')


# Run the main script
if __name__ == '__main__':
    # Create a Pinecone index
    create_index()

    # Insert a single item into the Pinecone index
    insert_items(r'D:\vscode\Medicine-chat-AI\data\medicines_output_medicines_en.xlsx')

    # # Search for similar items in the Pinecone index
    # search_items('1')

    # # Delete a single item from the Pinecone index
    # delete_item('1')

    # # Delete the Pinecone index
    # delete_index()
