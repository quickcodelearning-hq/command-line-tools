#!/bin/zsh
set -euo pipefail
(( $# == 0 )) || { print -u2 'Usage: ./install.sh'; exit 1; }
source_dir="${0:A:h}"
target="$HOME/.local/bin/lshed"
[[ -x "$source_dir/lshed" ]] || { print -u2 'Executable lshed missing beside installer'; exit 1; }
mkdir -p -- "$HOME/.local/bin"
if [[ -L "$target" && "$(readlink "$target")" == "$source_dir/lshed" ]]; then
    print 'lshed is already installed.'
elif [[ -e "$target" || -L "$target" ]]; then
    print -u2 -r -- "Refusing to replace existing path: $target"
    exit 1
else
    ln -s -- "$source_dir/lshed" "$target"
    print -r -- "Installed: $target -> $source_dir/lshed"
fi
case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) print 'Add this line to ~/.zshrc, then open a new terminal:'
       print 'export PATH="$HOME/.local/bin:$PATH"' ;;
esac
