---
name: trello-cli
description: Drive Trello from the command line with the `trello` CLI — read and write boards, lists, cards, checklists, labels, members, comments, due dates, webhooks and every other Trello REST endpoint. Use when the task mentions Trello, a Trello board or card, a trello.com URL, or asks to track/triage/move work items on a Trello board.
---

# Trello CLI

`trello` is a Go CLI covering the complete Trello REST API (261 endpoints). It is
the right tool whenever a task touches Trello: it authenticates for you, turns
names into ids, and speaks JSON.

## Before anything else

```sh
trello auth status
```

- Exit 0 → you are signed in; the output names the member and the profile.
- Exit 3 → not signed in. **Stop and tell the user.** They must run
  `trello auth login` themselves (it needs a browser) or export
  `TRELLO_API_KEY` and `TRELLO_TOKEN`. Never invent credentials, and never write
  a token into a file or a commit.
- `command not found` → the CLI is not installed. Suggest
  `go install github.com/quental/trello-cli/cmd/trello@latest`.

## The five rules

**1. Ask for JSON whenever you will read the answer.**

The default output is an aligned table meant for a human's eyes; it truncates
long values and colours them. Parsing it is a bug waiting to happen.

```sh
trello card ls --list "To Do" -o json          # parse this
trello card ls --list "To Do" --field name     # or just the field you need
trello card ls --list "To Do" -o id            # or just ids, to pipe
```

**2. Use names, not ids.**

Boards, lists, cards, labels, members and workspaces all resolve by name, by
trello.com URL, or by shortlink. `me` is you. There is no reason to look an id
up first.

```sh
trello card mv "Fix the login bug" --list "Done"
trello card assign "Ship v2" me
trello card show https://trello.com/c/aBcD1234
```

If a name is ambiguous the CLI fails and prints the candidates. Read them, pick
one, and re-run with the fuller name — do not guess an id.

**3. Set the board once.**

```sh
trello use board "Engineering"
```

Everything afterwards defaults to that board, so `trello list ls` and
`trello card ls --list "To Do"` need no `--board`. Use `--board "<name>"` on a
single command to override it without changing the default.

**4. Discover commands instead of guessing them.**

```sh
trello docs endpoints checklist     # every command touching checklists
trello card --help                  # what you can do to a card
trello card create --help           # every flag, and the endpoint it calls
```

Each help page names the REST endpoint it calls, so you can map back to
Trello's own documentation.

**5. Confirm before destroying anything.**

`delete` is permanent; `archive` is not. Prefer archiving. Destructive commands
prompt, and refuse to run unattended without `--yes` — that refusal is a
feature. Ask the user before passing `--yes`.

```sh
trello card archive "Old card"      # reversible, safe
trello card delete "Old card" --yes # permanent, ask first
```

## The commands you will reach for

```sh
# Orientation
trello me                                   # who am I
trello board ls                             # boards I can see
trello list ls                              # lists on the current board
trello card ls --list "In Progress"         # cards in a list
trello card ls --member me --overdue        # my overdue work
trello card show "Fix the login bug"        # one card, in full

# Writing
trello card create "Fix the login bug" --list "To Do" --due friday --label bug
trello card mv "Fix the login bug" --list "In Progress"
trello card comment "Fix the login bug" "root caused, fix in #421"
trello card assign "Fix the login bug" alice
trello card label "Fix the login bug" bug
trello card due "Fix the login bug" +3d
trello card due "Fix the login bug" --complete
trello card archive "Fix the login bug"

# Finding
trello search "login bug"
trello search "@me is:open due:week"
trello search "label:bug" --in-board "Engineering"
```

Dates accept `today`, `tomorrow`, `friday`, `next monday`, `+3d`, `+2w`, `+4h`,
`2026-08-15`, `2026-08-15T17:00`, and `none` to clear.

## Seeing the images on a card

Screenshots and mockups are often where a card's real content lives, but
a card listing gives you only their names and URLs. To actually look at one,
download it and then open the file with your own image-reading tool.

```sh
trello card attachments "Ship v2"                          # what is attached
trello card attachments download "Ship v2" --all --out ./trello-files
```

The path of every file written goes to stdout, so you can take it directly:

```sh
trello card attachments download "Ship v2" --all --out ./tmp --field path
```

Then read those paths as images. That two-step — download, then open — is the
whole trick; there is no way to see the picture without it.

- `--all` downloads every uploaded attachment and skips link attachments, which
  are just URLs pointing elsewhere and have no file to fetch.
- `--preview` fetches Trello's largest generated thumbnail instead of the
  original. For photos and screenshots it is a fraction of the size and usually
  enough to read. Prefer it unless you need fine detail.
- Name one attachment instead of `--all` to fetch just that file.
- Clean up the files when you are done; they are not yours to leave behind.

**Do not curl the `url` from `trello card attachments`.** Trello serves
attachment content only to a request carrying an OAuth `Authorization` header,
so a plain fetch of that URL returns 401 no matter what credentials you append
to it. The download command is the supported way in.

## Anything not listed above

Every one of the 261 endpoints has a command, organised by the object it acts
on: `action board card checklist customfield emoji enterprise label list member
notification powerup search token webhook workspace`.

```sh
trello docs endpoints <keyword>      # find the command
trello <noun> --help                 # browse a noun
```

If an endpoint accepts a parameter the command does not declare, add it:

```sh
trello board cards "Engineering" --param since=2026-07-01 --param limit=200
```

And any URL at all is reachable directly:

```sh
trello api /boards/aBcD1234/cards filter=open fields=name,due
trello api -X POST /cards name="New card" idList=<list-id>
```

## Reading errors

The CLI's errors are written to be acted on — read the whole message, including
the `Hint:` line. Exit codes:

| Code | Meaning | What to do |
|---|---|---|
| 0 | Success | — |
| 1 | Something else failed | Read the message |
| 2 | You declined a confirmation | — |
| 3 | Unauthorised / forbidden | Token missing, expired, or lacking write scope — tell the user |
| 4 | Not found | The object does not exist or the token cannot see it |
| 5 | Rate limited | The CLI already retried; slow down or batch |

## Pitfalls

- **Do not parse the table output.** Rule 1.
- **Quote names with spaces.** `--list "In Progress"`, not `--list In Progress`.
- **`me` is not an id.** It works as a value for member flags, and the CLI
  turns it into your real id where the API needs one. Do not substitute it
  yourself.
- **Status messages are on stderr, data is on stdout.** `trello card create … -o
  json > card.json` gives you clean JSON; the "✓ Created" line does not land in
  the file.
- **A list name only means something inside a board.** Two boards can both have
  "Done". Set `trello use board`, or pass `--board`. The same goes for
  checklists and their items, which need `--card`.
- **Archived objects are found only when nothing open matches.** If you meant
  the archived one, pass its id.
- **An attachment URL is not fetchable on its own.** Curling it returns 401;
  use the `card attachments download` command instead.
- **Batch with `-o id` and `xargs`, not with a loop of name lookups** — each
  lookup costs an API call, and Trello rate-limits at 100 requests per 10
  seconds per token.

## More detail

- `references/recipes.md` — worked examples: triage, standups, bulk edits,
  syncing from a repo, webhooks.
- `references/commands.md` — all 261 commands, generated from the CLI.
- `references/output.md` — every output format and how to shape it.
- `references/troubleshooting.md` — what each error means and what to do.
