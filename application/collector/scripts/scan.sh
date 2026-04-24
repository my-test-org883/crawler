#!/bin/bash

export CLI_URL=${CLI_URL:-https://example.com}

init.config ()
{
  export DOWNLOAD_URL=${DOWNLOAD_URL:-${CLI_URL}/cli/get-cli}
}

init.cli ()
{
  curl --silent "${DOWNLOAD_URL}" | bash
}

main.scan ()
{
  init.config
  init.cli
}

if [ "${0}" = "${BASH_SOURCE[0]}" ]; then
  set -e
  set -o pipefail
  set -u

  main.scan
fi