import requests
from st2actions.runners.pythonrunner import Action

class CreateGitHubIssueAction(Action):
    def run(self, title, body, labels=None, repo=None):
        token = self.config['token']
        if not repo:
            repo = self.config.get('repository')
            if not repo:
                raise Exception("Aucun dépôt spécifié dans la config ou en 
paramètre")
        
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "title": title,
            "body": body,
            "labels": labels if labels else []
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return {"status": "success", "issue_url": 
response.json()['html_url']}
        else:
            raise Exception(f"Erreur GitHub: {response.status_code} - 
{response.text}")
