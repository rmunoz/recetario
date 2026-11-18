#!/usr/bin/env bash
# Instala los git hooks versionados en scripts/ dentro de .git/hooks.
# Ejecutar una vez tras clonar el repositorio: scripts/install-hooks.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

ln -sf ../../scripts/pre-commit .git/hooks/pre-commit
echo "Hook de pre-commit instalado."
