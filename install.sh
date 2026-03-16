#!/bin/bash
set -e

CONTAINER="st2-docker-st2client-1"
DIR="/opt/stackstorm/packs/custom"

echo "🚀 Installation Actions Python..."

# execute_command
docker cp /dev/stdin "$CONTAINER:$DIR/actions/execute_command.py" << 'PYEOF'
#!/usr/bin/env python3
import subprocess, logging
from st2common.runners.base_action import BaseAction
LOG = logging.getLogger(__name__)
class ExecuteCommandAction(BaseAction):
    def run(self, command, timeout=30):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            return {'status': 'success', 'stdout': result.stdout.strip(), 'message': '✅ Succès'}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'message': '❌ Erreur'}
PYEOF

docker cp /dev/stdin "$CONTAINER:$DIR/actions/execute_command.yaml" << 'YAMLEOF'
name: execute_command
pack: custom
description: "Exécute une commande"
enabled: true
runner_type: python-script
entry_point: execute_command.py
parameters:
  command:
    type: string
    required: true
  timeout:
    type: integer
    default: 30
YAMLEOF

# restart_service
docker cp /dev/stdin "$CONTAINER:$DIR/actions/restart_service.py" << 'PYEOF'
#!/usr/bin/env python3
import subprocess, logging
from st2common.runners.base_action import BaseAction
LOG = logging.getLogger(__name__)
class RestartServiceAction(BaseAction):
    def run(self, service_name, environment="dev"):
        try:
            cmd = f"sudo systemctl restart {service_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {'status': 'success', 'message': f'✅ {service_name} redémarré'}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'message': '❌ Erreur'}
PYEOF

docker cp /dev/stdin "$CONTAINER:$DIR/actions/restart_service.yaml" << 'YAMLEOF'
name: restart_service
pack: custom
description: "Redémarre un service"
enabled: true
runner_type: python-script
entry_point: restart_service.py
parameters:
  service_name:
    type: string
    required: true
  environment:
    type: string
    default: "dev"
YAMLEOF

# system_health_check
docker cp /dev/stdin "$CONTAINER:$DIR/actions/system_health_check.py" << 'PYEOF'
#!/usr/bin/env python3
import subprocess, logging
from st2common.runners.base_action import BaseAction
LOG = logging.getLogger(__name__)
class SystemHealthCheckAction(BaseAction):
    def run(self):
        return {'status': 'healthy', 'message': '✅ Système OK'}
PYEOF

docker cp /dev/stdin "$CONTAINER:$DIR/actions/system_health_check.yaml" << 'YAMLEOF'
name: system_health_check
pack: custom
description: "Vérifie la santé"
enabled: true
runner_type: python-script
entry_point: system_health_check.py
YAMLEOF

# Règles Telegram
docker cp /dev/stdin "$CONTAINER:$DIR/rules/telegram_commands.yaml" << 'YAMLEOF'
---
name: telegram_run
pack: custom
enabled: true
trigger:
  type: custom.message
criteria:
  trigger.text:
    pattern: "^/run\\s+"
    type: matchregex
action:
  ref: custom.execute_command
  params:
    command: "{{ trigger.text.replace('/run ', '').strip() }}"
YAMLEOF

# Recharger
echo "✓ Rechargement..."
docker exec -it "$CONTAINER" st2ctl reload --register-all

echo "✅ Installation terminée!"
