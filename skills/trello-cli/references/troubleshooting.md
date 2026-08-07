# When something goes wrong

The CLI's errors are written to be read. Every one of them ends with a `Hint:`
line when there is something concrete to do. Read the whole message before
retrying.

## "no Trello credentials configured"

Nothing is signed in. `TRELLO_API_KEY` and `TRELLO_TOKEN` are not set and the
config file has no token for the active profile.

**Do not try to fix this yourself.** Tell the user to run `trello auth login`,
which needs a browser. In CI, they must export both variables.

```sh
trello auth status          # exit 3 means not signed in
trello config path          # where the config would be written
```

## `"X" matches N boards; be more specific or pass an id`

Two objects answer to the same name. The error lists them with their ids. Pick
one and re-run with the fuller name, or with the id.

```console
$ trello board get "Team"
error: "Team" matches 2 boards; be more specific or pass an id:
  5abbe4b7ddc1b351ef961414  Team Alpha  (open)
  5abbe4b7ddc1b351ef961415  Team Beta   (open)

$ trello board get "Team Alpha"
```

## `no list named "X"` … `Available: …`

The name does not exist in the board that is in scope. Two usual causes:

1. **The wrong board is in scope.** A list name only means something inside a
   board. Check with `trello use`, and pass `--board "<name>"` to override.
2. **The object is archived.** Archived objects are matched only when nothing
   open matches. Pass the id, or add `--filter all` on the listing command.

## `cannot resolve list "X": no board in scope`

Nothing told the CLI which board to look in.

```sh
trello use board "Engineering"          # once, persists
trello list ls --board "Engineering"    # or per command
```

## Exit 3 — `Trello API error 401` / `403`

- **401**: the token is missing, expired, or was revoked. A new one is needed.
- **403**: the token is real but not allowed to do this. Most often it was
  minted read-only, and you are trying to write. `trello auth login --scope
  read,write,account` mints a writable one. Some endpoints also need board
  admin, a paid plan, or an Enterprise.

Neither is something you can work around. Report it.

## Exit 4 — `Trello API error 404`

The object does not exist, or the token cannot see it. A board you were removed
from returns 404, not 403. Confirm with `trello board ls` or `trello search`.

## Exit 5 — `Trello API error 429`

Rate limited, after the CLI already retried with backoff. Trello allows 300
requests per 10 seconds per API key and 100 per token.

If you are looping over objects, you are making one request per iteration plus
one per name lookup. Fix it by resolving once and reusing ids:

```sh
# Costly: a name lookup per card
for name in "$@"; do trello card archive "$name"; done

# Cheap: one listing, then one call per card
trello card ls --list "Done" -o id | xargs -n1 trello card archive -y
```

## `400 Bad Request: invalid id`

A value that should be an id is not one. Usually it means a name was passed
somewhere the CLI does not resolve — a parameter it does not know is an id.
Resolve it yourself and pass the id:

```sh
board=$(trello board ls --field id --columns id | head -1)
trello api /boards/$board/cards
```

## A command exists but a parameter is missing

The OpenAPI document Trello publishes is incomplete for some endpoints. Add the
parameter directly:

```sh
trello board cards "Engineering" --param since=2026-07-01 --param limit=200
```

Or call the endpoint yourself:

```sh
trello api /boards/aBcD1234/cards since=2026-07-01
```

## The output looks wrong or truncated

You are reading the human table. Ask for data:

```sh
trello card ls --list "To Do" -o json
```

Table cells are truncated to keep columns aligned when writing to a terminal.
Piped output is not truncated, but it is still a table.

## Stale names

Board, list, label and member listings are cached for 10 minutes to keep name
resolution cheap. After renaming something in the Trello UI:

```sh
trello config cache-clear
# or, for one command
trello --no-cache list ls
```

## Seeing what is actually sent

```sh
trello --debug card ls --list "To Do"
```

Every request is traced to stderr with its method, URL (credentials redacted),
status, duration and response size.

## Two accounts at once

```sh
trello --profile work auth login
trello --profile work board ls
trello config profiles
```
