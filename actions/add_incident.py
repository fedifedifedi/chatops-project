import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from st2actions.runners.pythonrunner import Action
import uuid

class AddIncidentAction(Action):
    def run(self, description, solution, service=None, severity=None):
        client = chromadb.HttpClient(host='host.docker.internal', port=8000)
        collection = client.get_or_create_collection(name="incidents")
        incident_id = str(uuid.uuid4())
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(description).tolist()
        metadata = {
            "solution": solution,
            "service": service if service else "",
            "severity": severity if severity else "",
            "description": description
        }
        collection.add(
            ids=[incident_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[description]
        )
        return {"status": "success", "id": incident_id}
