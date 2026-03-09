import requests
import json
from st2actions.runners.pythonrunner import Action

class TelegramSearchAction(Action):
    def run(self, message, chat_id):
        # Extraire la requête (enlever "/search ")
        query = message.replace("/search ", "", 1).strip()
        
        if not query:
            self._send_telegram(chat_id, "🔍 Veuillez fournir une 
recherche. Exemple: /search postgres lent")
            return {"success": True, "message": "Requête vide"}
        
        # Rechercher dans Qdrant
        search_result = self._search_qdrant(query)
        
        if not search_result["success"]:
            self._send_telegram(chat_id, f"❌ Erreur de recherche: 
{search_result['error']}")
            return search_result
        
        # Formater les résultats
        incidents = search_result["incidents"]
        
        if not incidents:
            self._send_telegram(chat_id, f"🔍 Aucun incident similaire 
trouvé pour: '{query}'")
            return {"success": True, "message": "Aucun résultat"}
        
        # Construire le message Telegram
        message_text = f"🔍 *Résultats pour:* {query}\n\n"
        
        for i, inc in enumerate(incidents[:5], 1):  # Max 5 résultats
            payload = inc.get("payload", {})
            message_text += f"*{i}. {payload.get('description', 
'N/A')}*\n"
            message_text += f"   📌 Service: {payload.get('service', 
'N/A')}\n"
            message_text += f"   ⚠️ Gravité: {payload.get('severity', 
'N/A')}\n"
            message_text += f"   ✅ Solution: {payload.get('solution', 
'N/A')}\n\n"
        
        # Envoyer à Telegram
        self._send_telegram(chat_id, message_text)
        
        return {"success": True, "incidents": incidents}
    
    def _search_qdrant(self, query):
        """Recherche dans Qdrant"""
        url = "http://qdrant:6333/collections/incidents/points/search"
        
        # Vecteur factice (à améliorer avec des embeddings plus tard)
        payload = {
            "vector": [0.1] * 384,
            "limit": 5,
            "with_payload": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return {
                    "success": True,
                    "incidents": response.json().get("result", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_telegram(self, chat_id, text):
        """Envoie un message Telegram"""
        bot_token = "8433180991:AAGPaycy4Ng4V_aXg3Ocpm6NPdBEsjHvxkI"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            requests.post(url, json=payload, timeout=5)
        except:
            pass  # Ignorer les erreurs d'envoi
