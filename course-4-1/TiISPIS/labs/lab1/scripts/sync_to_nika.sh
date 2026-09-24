#!/usr/bin/env bash
# Копирует фрагменты БЗ предметной области «Музыка» в локальный клон NIKA.
# Запуск из корня lab1: ./scripts/sync_to_nika.sh
# Опционально: NIKA_ROOT=/path/to/nika ./scripts/sync_to_nika.sh
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd "$script_dir/.." && pwd)"
src="$lab_dir/kb/extra/section_subject_domain_of_music"
nika_root="${NIKA_ROOT:-$(cd "$lab_dir/../nika" 2>/dev/null && pwd || true)}"

if [[ -z "${nika_root}" || ! -d "$nika_root/kb/extra" ]]; then
  echo "Не найден клон NIKA. Укажите NIKA_ROOT или клонируйте в labs/nika:" >&2
  echo "  git clone -b tpis-2023 --recursive https://github.com/ostis-apps/nika labs/nika" >&2
  exit 1
fi

dest="$nika_root/kb/extra/section_subject_domain_of_music"
mkdir -p "$nika_root/kb/extra"
rm -rf "$dest"
cp -a "$src" "$dest"
echo "Скопировано: $src -> $dest"
echo "Далее в каталоге NIKA пересоберите БЗ:"
echo "  docker compose run --rm --entrypoint \"\" problem-solver bash -lc \\"
echo "    'export BINARY_PATH=/nika/bin BUILD_PATH=/nika/build CONFIG_PATH=/nika/nika.ini KB_PATH=../repo.path; /nika/scripts/build_kb.sh'"
echo "или просто: docker compose up --no-build  (REBUILD_KB=1)"
