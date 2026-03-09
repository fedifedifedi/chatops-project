import requests
from st2actions.runners.pythonrunner import Action

class CheckCiStatusAction(Action):
    def run(self, repo, commit_sha, branch="main"):
        # Récupérer le token GitHub depuis Vault
        token_result = self._get_github_token()
        
        if not token_result['success']:
            return token_result
        
        # Vérifier le statut CI
        status = self._check_commit_status(repo, commit_sha, 
token_result['token'])
        
        # Notifier Telegram
        self._notify_telegram(repo, branch, commit_sha[:7], status)
        
        return status
    
    def _get_github_token(self):
        """Récupère le token GitHub depuis Vault"""
        try:
            # Utiliser l'action Vault existante
            result = self.action_service.call_action(
                'custom.read_vault', 
                {"path": "github"}
            )
            
            if result and result.get('success'):
                return {
                    "success": True, 
                    "token": result.get('token')
                }
            return {
                "success": False, 
                "message": "Token non trouvé"
            }
        except Exception as e:
            return {
                "success": False, 
                "message": str(e)
            }
    
    def _check_commit_status(self, repo, sha, token):
        """Interroge l'API GitHub pour le statut CI"""
        url = f"https://api.github.com/repos/{repo}/commits/{sha}/status"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "repo": repo,
                    "sha": sha,
                    "state": data.get('state'),  # success, failure, 
pending
                    "statuses": data.get('statuses', [])
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
    
    def _notify_telegram(self, repo, branch, sha_short, status):
        """Envoie une notification Telegram"""
        if not status.get('success'):
            message = f"❌ Erreur vérification CI: {status.get('error', 
'inconnue')}"
        elif status.get('state') == 'success':
            message = f"✅ CI réussi: {repo} ({branch}) - {sha_short}"
        elif status.get('state') == 'failure':
            message = f"❌ CI échoué: {repo} ({branch}) - {sha_short}"
        else:
            message = f"⏳ CI en cours: {repo} ({branch}) - {sha_short}"
        
        # Utiliser l'action Telegram existante
        self.action_service.call_action('custom.telegram_send_message', {
            'message': message,
            'chat_id': '8631806428'  # Votre chat_id
        })
