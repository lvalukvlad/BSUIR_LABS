#!/usr/bin/env bash
# Рендер диаграмм PlantUML в PNG.
# Пути отсчитываются от расположения скрипта. При первом запуске
# берёт ~/.local/share/plantuml/plantuml.jar или качает jar рядом со скриптом.
#
# Запуск: ./scripts/render-diagrams.sh
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
report_dir="$(cd "$script_dir/.." && pwd)"
source_dir="$report_dir/plantuml"
target_dir="$report_dir/png"
local_jar="$script_dir/plantuml.jar"
global_jar="${PLANTUML_JAR:-$HOME/.local/share/plantuml/plantuml.jar}"
jar_url="https://github.com/plantuml/plantuml/releases/download/v1.2025.4/plantuml-1.2025.4.jar"

if ! command -v java >/dev/null; then
  echo "Java не найдена в PATH. Установите JRE и повторите запуск." >&2
  exit 1
fi

jar=""
if [[ -f "$local_jar" ]]; then
  jar="$local_jar"
elif [[ -f "$global_jar" ]]; then
  jar="$global_jar"
else
  echo "Загрузка plantuml.jar..."
  curl -fsSL "$jar_url" -o "$local_jar"
  jar="$local_jar"
fi

mkdir -p "$target_dir"
shopt -s nullglob
sources=("$source_dir"/*.puml)
if [[ ${#sources[@]} -eq 0 ]]; then
  echo "В каталоге $source_dir нет файлов .puml" >&2
  exit 1
fi

echo "Рендер ${#sources[@]} диаграмм в $target_dir"
java -jar "$jar" -charset UTF-8 -tpng -o "$target_dir" "${sources[@]}"
for png in "$target_dir"/*.png; do
  [[ -f "$png" ]] || continue
  printf '  %s (%s байт)\n' "$(basename "$png")" "$(wc -c < "$png")"
done
