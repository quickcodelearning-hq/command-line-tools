# At The Books folder shortcut
atb() {
  emulate -L zsh
  local base="/Users/kennethlowrey/Documents/At The Books"
  if (( $# == 0 )); then
    builtin cd -- "$base"
    return $?
  fi
  if (( $# != 1 )) || [[ -z "$1" || "$1" == *[^0-9]* ]]; then
    print -u2 -- "Usage: atb [chapter number] — for example: atb 27"
    return 1
  fi
  if [[ ! -d "$base" ]]; then
    print -u2 -- "atb: Books folder not found: $base"
    return 1
  fi
  local chapter="$1" folder suffix
  while [[ ${#chapter} -gt 1 && "$chapter" == 0* ]]; do
    chapter="${chapter#0}"
  done
  local -a matches=()
  for folder in "$base"/ATB*CH*(N/); do
    suffix="${folder##*CH}"
    [[ -n "$suffix" && "$suffix" != *[^0-9]* ]] || continue
    while [[ ${#suffix} -gt 1 && "$suffix" == 0* ]]; do
      suffix="${suffix#0}"
    done
    [[ "$suffix" == "$chapter" ]] && matches+=("$folder")
  done
  if (( ${#matches} == 0 )); then
    print -u2 -- "atb: No folder beginning with ATB and ending with CH$chapter found in $base."
    return 1
  elif (( ${#matches} > 1 )); then
    print -u2 -- "atb: Multiple folders match chapter $chapter; staying in the current folder:"
    printf >&2 '  %s\n' "${matches[@]}"
    return 1
  fi
  local destination="${matches[1]}"
  if [[ -d "$destination/Export" ]]; then
    destination="$destination/Export"
  fi
  builtin cd -- "$destination"
}
