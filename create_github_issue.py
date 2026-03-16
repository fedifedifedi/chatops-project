import requests
import hvac
from st2actions.runners.pythonrunner import Action

class CreateGitHubIssueAction(Action):
    def run(self, title, description, labels, chat_id):
        try:
            # Lire le token GitHub depuis Vault
            client = hvac.Client(url='http://host.docker.internal:8200', token='root')
            secret = client.secrets.kv.v2.read_secret_version(
                mount_point='secret',
                path='github'
            )
            token = secret['data']['data']['token']
            
            # Créer l'issue GitHub
            repo = "fedifedifedi/chatops-project"
            url = f"https://api.github.com/repos/{repo}/issues"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "title": title,
                "body": description,
                "labels": labels.split(',') if labels else []
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                issue = response.json()
                issue_url = issue['html_url']
                
                # Notification Telegram
                self._send_telegram_notification(chat_id, issue_url, title)
                
                return {
                    "success": True,
                    "issue_url": issue_url,
                    "issue_number": issue['number'],
                    "message": f"✅ Issue créée: {issue_url}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Erreur {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_telegram_notification(self, chat_id, issue_url, title):
        """Envoie une notification Telegram"""
        try:
            # Lire le token Telegram depuis Vault
            client = hvac.Client(url='http://host.docker.internal:8200', token='root')
            secret = client.secrets.kv.v2.read_secret_version(
                mount_point='secret',
                path='telegram'
            )
            token = secret['data']['data']['token']
            
            # Envoyer le message
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            message = f"✅ **Issue GitHub créée !**\n\n📝 {title}\n🔗 {issue_url}"
            
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data, timeout=10)
            print(f"Telegram notification sent: {response.status_code}")
        except Exception as e:
            print(f"Erreur notification Telegram: {e}")
