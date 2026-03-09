import chromadb
from sentence_transformers import SentenceTransformer
from st2actions.runners.pythonrunner import Action

class SearchSimilarIncidentsAction(Action):
    def run(self, query, top_k=5):
        client = chromadb.HttpClient(host='host.docker.internal', port=8000)
        collection = client.get_or_create_collection(name="incidents")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        incidents = []
        for i in range(len(results['ids'][0])):
            incidents.append({
                "id": results['ids'][0][i],
                "description": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        return incidents
