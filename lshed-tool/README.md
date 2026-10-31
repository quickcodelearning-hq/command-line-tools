# Lead Shredder shortcuts

Lightweight Zsh wrapper using the existing application's `.venv/bin/python`.
No dependencies are installed; no activation is needed. Default application:
`~/Documents/code/lead-shedder`. Override with `LSHED_APP_DIR` if needed.

## Install

```sh
cd /Users/kennethlowrey/Documents/code/command-line-tools/lshed-tool
./install.sh
```

The installer creates `~/.local/bin/lshed`, is safe to repeat, and refuses to
replace another file or symlink. Keep this utility directory in place.
If `~/.local/bin` is not on PATH, add this line once to `~/.zshrc`:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

Open a new terminal (or run that export now), then use `lshed help` anywhere.
The installer does not edit shell configuration. To uninstall, remove only
`~/.local/bin/lshed` after checking that it points to this utility.

## Commands

| Command | Behavior |
| --- | --- |
| `help` | Show usage; also the default with no arguments |
| `run` | `export`, default limit 25; writes CSV/history and makes Google/email requests |
| `dry-run` | `export --dry-run`; **still calls Google**, but skips email lookup and CSV/history writes |
| `enrich` | `enrich-emails`, default limit 100; updates historical SQLite/CSV email fields |
| `retry-emails` | `enrich-emails --retry-checked`; retains the application's cooldown and attempt caps |
| `history` | Read-only total and unique practice counts; never creates/migrates the DB |
| `test` | Existing application's mocked unittest suite with temporary data |
| `status` | Local paths, CSV count, and read-only history totals |
| `doctor` | Local venv/dependency/file checks and API-key presence; no network or secret output |

```sh
lshed run --limit 10 --city "Fort Lauderdale, FL"
lshed dry-run --limit 5
lshed enrich --limit 100
lshed retry-emails --limit 100
lshed status
lshed doctor
lshed test
```

The first four commands forward arguments, including `--help`, to the app.
All operations run from the application directory so the default database and
exports stay consistent from any caller directory. Relative `--db` and
`--export-dir` options therefore resolve there; use absolute paths for other data.
`GOOGLE_API_KEY` is inherited from the shell, never loaded from a file or printed.
An unset key is informational in doctor because local and enrichment commands do
not need it. Doctor checks presence, not API validity. No reset shortcut is exposed.

## Offline verification

```sh
/bin/zsh -n lshed install.sh
/Users/kennethlowrey/Documents/code/lead-shedder/.venv/bin/python -B test_wrapper.py
./lshed test
```

Wrapper tests use a fake application, temporary HOME, and temporary database.
They check dispatch/quoting, exit codes, invalid commands, read-only history,
installation from a path containing spaces, repeat installation, conflict
preservation, and invocation via the symlink from another directory.
The application's tests mock HTTP and use temporary data. Do not run actual
`run`, `dry-run`, `enrich`, or `retry-emails` for offline verification.
