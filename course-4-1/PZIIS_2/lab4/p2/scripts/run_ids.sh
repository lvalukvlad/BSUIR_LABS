#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p logs pcaps snort
cp -n /etc/snort/classification.config snort/classification.config
cp -n /etc/snort/reference.config snort/reference.config

python3 scripts/make_pcap.py
rm -f logs/alert logs/snort.out
mkdir -p logs

(
  cd snort
  snort -k none -A fast -c snort.conf -r ../pcaps/lab4.pcap -l ../logs \
    > ../logs/snort.out 2>&1 || true
)

python3 scripts/analyze_alerts.py
echo "alert: $(wc -l < logs/alert 2>/dev/null || echo 0) строк"
