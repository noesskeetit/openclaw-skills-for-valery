#!/usr/bin/env bash
#
# skill-ssh-wrapper.sh
#
# Runs on the VM. SSHes back to the Mac via reverse tunnel
# and executes Docker commands for OpenClaw skills.
#
# Usage:
#   ./skill-ssh-wrapper.sh <skill> <sub-command> <argument>
#
# Examples:
#   ./skill-ssh-wrapper.sh code-runner python "print('hello')"
#   ./skill-ssh-wrapper.sh web-browser browse "https://example.com"
#   ./skill-ssh-wrapper.sh web-search searxng "Python programming"
#   ./skill-ssh-wrapper.sh diagram-generator graphviz "digraph { A -> B }"

set -euo pipefail

SSH_KEY="$HOME/.ssh/mac_key"
SSH_USER="aogabbasov"
SSH_HOST="localhost"
SSH_PORT="2222"

SKILL="${1:-}"
SUBCMD="${2:-}"
ARG="${3:-}"

# --- Validation -----------------------------------------------------------

if [[ -z "$SKILL" ]]; then
    echo "Error: skill name is required" >&2
    echo "Usage: $0 <skill> <sub-command> <argument>" >&2
    exit 1
fi

if [[ -z "$SUBCMD" ]] && [[ "$SKILL" != "document-analyzer" ]] && [[ "$SKILL" != "document-creator" ]]; then
    echo "Error: sub-command is required for skill '$SKILL'" >&2
    echo "Usage: $0 <skill> <sub-command> <argument>" >&2
    exit 1
fi

# For document-analyzer and document-creator the sub-command slot carries the argument
if [[ "$SKILL" == "document-analyzer" ]] || [[ "$SKILL" == "document-creator" ]]; then
    ARG="${SUBCMD}"
    SUBCMD=""
fi

if [[ -z "$ARG" ]] && [[ "$SKILL" != "document-analyzer" ]] && [[ "$SKILL" != "document-creator" ]]; then
    echo "Error: argument is required" >&2
    echo "Usage: $0 <skill> <sub-command> <argument>" >&2
    exit 1
fi

# --- Build remote command --------------------------------------------------

build_remote_cmd() {
    local skill="$1"
    local subcmd="$2"
    local arg="$3"

    # Escape single quotes inside the argument for safe shell embedding
    local escaped_arg="${arg//\'/\'\\\'\'}"

    case "${skill}/${subcmd}" in

        code-runner/python)
            echo "docker run --rm openclaw-code-runner scripts/run_python.py -c '${escaped_arg}'"
            ;;

        code-runner/node)
            echo "docker run --rm --entrypoint python3 openclaw-code-runner scripts/run_node.py -c '${escaped_arg}'"
            ;;

        web-browser/browse)
            echo "docker run --rm openclaw-web-browser scripts/browse.py '${escaped_arg}'"
            ;;

        web-browser/extract)
            echo "docker run --rm openclaw-web-browser scripts/extract_content.py '${escaped_arg}'"
            ;;

        web-browser/screenshot)
            echo "docker run --rm -v /tmp:/output openclaw-web-browser scripts/screenshot.py '${escaped_arg}' -o /output/screenshot.png"
            ;;

        web-search/searxng)
            echo "SEARXNG_URL=http://localhost:8888 python3 ~/cloud_code_project/openclaw-skills/web-search-searxng/scripts/search.py '${escaped_arg}'"
            ;;

        diagram-generator/graphviz)
            echo "echo '${escaped_arg}' | docker run --rm -i --platform linux/amd64 --entrypoint dot openclaw-diagram-generator -Tsvg"
            ;;

        diagram-generator/mermaid)
            echo "docker run --rm --platform linux/amd64 --entrypoint bash openclaw-diagram-generator -c \"echo '${escaped_arg}' > /tmp/d.mmd && python3 scripts/generate_mermaid.py /tmp/d.mmd -o /tmp/out.svg && cat /tmp/out.svg\""
            ;;

        document-analyzer/)
            echo "docker run --rm -v /tmp/skill-input:/input openclaw-document-analyzer -c '${escaped_arg}'"
            ;;

        document-creator/)
            echo "docker run --rm -v /tmp/skill-output:/output openclaw-document-creator -c '${escaped_arg}'"
            ;;

        *)
            echo ""
            ;;
    esac
}

REMOTE_CMD="$(build_remote_cmd "$SKILL" "$SUBCMD" "$ARG")"

if [[ -z "$REMOTE_CMD" ]]; then
    echo "Error: unknown skill/sub-command combination: ${SKILL}/${SUBCMD}" >&2
    echo "" >&2
    echo "Supported skills:" >&2
    echo "  code-runner      python | node" >&2
    echo "  web-browser      browse | extract | screenshot" >&2
    echo "  web-search       searxng" >&2
    echo "  diagram-generator graphviz | mermaid" >&2
    echo "  document-analyzer (no sub-command)" >&2
    echo "  document-creator  (no sub-command)" >&2
    exit 1
fi

# --- Execute via SSH -------------------------------------------------------

if ! ssh \
    -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 \
    -o BatchMode=yes \
    -p "$SSH_PORT" \
    "${SSH_USER}@${SSH_HOST}" \
    "$REMOTE_CMD"; then

    echo "Error: SSH connection to ${SSH_USER}@${SSH_HOST}:${SSH_PORT} failed" >&2
    echo "Make sure the reverse SSH tunnel is active and the key is in place." >&2
    exit 2
fi
