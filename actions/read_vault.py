import hvac
from st2actions.runners.pythonrunner import Action

class ReadVaultAction(Action):
    def run(self, path):
        client = hvac.Client(url='http://host.docker.internal:8200', 
token='root-token')
        secret = client.read(path)
        if secret is None:
            raise Exception(f"Secret {path} not found")
        # Pour KV v2, les données sont dans secret['data']['data']
        # On retourne tout pour voir
        return secret
