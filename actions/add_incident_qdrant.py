import requests
import uuid
from st2actions.runners.pythonrunner import Action

class AddIncidentQdrantAction(Action):
    def run(self, description, solution, service=None, severity=None):
        embedding = [0.0] * 384
        incident_id = str(uuid.uuid4())
        payload = {
            "id": incident_id,
            "vector": embedding,
            "payload": {
                "description": description,
                "solution": solution,
                "service": service if service else "",
                "severity": severity if severity else ""
            }
        }
        response = requests.put(
            f"http://qdrant:6333/collections/incidents/points",
            json={"points": [payload]}
        )
        if response.status_code == 200:
            return {"status": "success", "id": incident_id}
        else:
            raise Exception(f"Erreur Qdrant: {response.status_code} - {response.text}")
