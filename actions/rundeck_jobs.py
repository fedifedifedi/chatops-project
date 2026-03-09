import requests
from st2actions.runners.pythonrunner import Action

class RundeckJobsAction(Action):
    def run(self, action, project=None, job_id=None):
        url = "http://host.docker.internal:4440"
        token = "U9mKby2v8YNSHzVRlZLZWfe5zJxfkgKp"
        headers = {"X-Rundeck-Auth-Token": token, "Accept": 
"application/json"}

        if action == "list":
            if not project:
                raise Exception("Le paramètre 'project' est requis pour 
lister les jobs")
            api_url = f"{url}/api/14/project/{project}/jobs"
            response = requests.get(api_url, headers=headers)
        elif action == "run":
            if not job_id:
                raise Exception("Le paramètre 'job_id' est requis pour 
exécuter un job")
            api_url = f"{url}/api/14/job/{job_id}/run"
            response = requests.post(api_url, headers=headers)
        else:
            raise Exception("Action non reconnue. Utilise 'list' ou 
'run'")

        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Erreur API Rundeck: {response.status_code} - 
{response.text}")
