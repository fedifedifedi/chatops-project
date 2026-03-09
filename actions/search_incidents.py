import requests
from st2actions.runners.pythonrunner import Action

class SearchIncidentsAction(Action):
    def run(self, query_text, top_k=5):
        # Pour le test, on utilise un vecteur de zéros
        # Idéalement, il faudrait transformer le texte en vecteur
        query_vector = [0.0] * 384
        
        response = requests.post(
            f"http://qdrant:6333/collections/incidents/points/search",
            json={
                "vector": query_vector,
                "limit": top_k,
                "with_payload": True
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erreur recherche: {response.status_code} - 
{response.text}")
