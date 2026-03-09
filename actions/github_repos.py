import requests
import hvac
from st2actions.runners.pythonrunner import Action

class GithubReposAction(Action):
    def run(self, username):
        # Récupérer le token depuis Vault
        client = hvac.Client(url='http://host.docker.internal:8200', 
token='root-token')
        secret = client.read('secret/data/github')
        import requests
import hvac
from st2actions.runners.pythonrunner import Action

class GithubReposAction(Action):
    def run(self, username):
        # Récupérer le token depuis Vault
        client = hvac.Client(url='http://host.docker.internal:8200', 
token='root-token')
        secret = client.read('secret/data/github')
        import requests
import hvac
from st2actions.runners.pythonrunner import Action

class GithubReposAction(Action):
    def run(self, username):
        # Récupérer le token depuis Vault
        client = hvac.Client(url='http://host.docker.internal:8200', 
token='root-token')
        secret = client.read('secret/data/github')
        token = secret['data']['data']['token']

        # Appel à l'API GitHub
        headers = {'Authorization': f'token {token}'}
        url = f'https://api.github.com/users/{username}/repos'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repos = response.json()
            return [{'name': repo['name'], 'url': repo['html_url']} for 
repo in repos]
        else:
            raise Exception(f"GitHub API error: {response.status_code} - 
{response.text}")
