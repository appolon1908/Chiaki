#!/usr/bin/env bash
set -euo pipefail

if git grep -nE '(regist_key|morning|oauth|psn.*token|account_id).*(=|:).*[A-Za-z0-9+/]{12,}' -- ':!nabeel/chiaki/preflight.sh' ':!docs' >/tmp/nabeel-chiaki-secrets.txt 2>/dev/null; then
  echo "NABEEL_CHIAKI_SECRET_SCAN=FAIL"
  cat /tmp/nabeel-chiaki-secrets.txt
  exit 1
fi

if command -v chiaki-ng >/dev/null 2>&1 || command -v chiaki >/dev/null 2>&1 || command -v chiaki4deck >/dev/null 2>&1; then
  echo "NABEEL_CHIAKI_RUNTIME=FOUND"
else
  echo "NABEEL_CHIAKI_RUNTIME=NOT_INSTALLED"
fi

origin="$(git remote get-url origin)"
upstream="$(git remote get-url upstream)"
[[ "$origin" == "https://github.com/ingtrader21-spec/Chiaki.git" ]]
[[ "$upstream" == "https://github.com/streetpea/chiaki-ng.git" ]]

echo "NABEEL_CHIAKI_GOVERNANCE=PASS"
echo "PAIRING_CREDENTIALS_COMMITTED=0"
