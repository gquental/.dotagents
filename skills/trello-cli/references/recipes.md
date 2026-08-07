# Recipes

Worked examples. Each one assumes `trello use board "<your board>"` has been run
once, so `--board` is implicit.

## Orientation

```sh
# What am I working with?
trello me --field username
trello board ls
trello list ls --counts
```

```sh
# A board's whole state, as JSON, in one call
trello api /boards/aBcD1234 \
  cards=open lists=open members=all labels=all \
  card_fields=name,due,idList,idMembers,labels -o json
```

That last one is worth knowing: Trello's *nested resource* parameters let one
request return a board with its lists, cards, labels and members embedded. It is
far cheaper than four calls, and `trello api` is the way to reach it.

## Daily triage

```sh
# What is overdue and mine
trello card ls --member me --overdue -o json

# What is due in the next two days
trello card ls --member me --due-soon --field name

# What is unassigned in the backlog
trello card ls --list "Backlog" -o json \
  | jq -r '.[] | select(.idMembers | length == 0) | .name'
```

## Creating work

```sh
# One card
trello card create "Fix the login bug" \
  --list "To Do" --due friday --label bug --member me \
  --desc "Reported by support. Repro: log in with an expired session."

# A card whose description is a file
trello card create "Design review" --list "To Do" --desc "$(cat notes.md)"

# A card with an attachment
trello card create "Mockups" --list "Design" --attach ./mock-v3.png

# A checklist on it
trello card checklists add "Fix the login bug" "Steps"
trello checklist check-items add "Steps" "Write a failing test"
trello checklist check-items add "Steps" "Fix the session refresh"
```

## Moving work along

```sh
trello card mv "Fix the login bug" --list "In Progress"
trello card comment "Fix the login bug" "PR up: https://github.com/acme/app/pull/421"
trello card mv "Fix the login bug" --list "Done" --position top
trello card due "Fix the login bug" --complete
```

## Bulk edits

Always go through `-o id`. One lookup, then one call per object.

```sh
# Archive everything in Done
trello card ls --list "Done" -o id | xargs -n1 trello card archive -y

# Label every overdue card
trello card ls --overdue -o id \
  | while read -r id; do trello card label "$id" "late"; done

# Move a whole list's cards elsewhere
trello list cards move "Backlog" --to-list "Up Next" --to-board "Engineering"
```

Trello allows 100 requests per 10 seconds per token. For more than ~50 objects,
add a small sleep or expect the CLI's automatic backoff to slow you down.

## Reporting

```sh
# Standup: what moved yesterday
trello board actions "Engineering" --filter updateCard --limit 50 -o json \
  | jq -r '.[] | "\(.memberCreator.username): \(.data.card.name)"'

# Cards created this week, as CSV
trello board cards "Engineering" --fields name,due,dateLastActivity -o csv > week.csv

# Who has how much in flight
trello card ls --list "In Progress" -o json \
  | jq -r '.[].idMembers[]' | sort | uniq -c | sort -rn
```

## Searching

Trello's search operators work verbatim:

```sh
trello search "@me is:open due:week"
trello search "label:bug -label:wontfix"
trello search "list:\"In Progress\" has:attachments"
trello search "created:14 sort:created"
trello search "board:Engineering @alice"
```

Add `--type boards,organizations,members` to search beyond cards.

## From a git repository

```sh
# Card for the current branch
branch=$(git rev-parse --abbrev-ref HEAD)
trello card create "$branch" --list "In Progress" --member me

# Comment the last commit onto a card
git log -1 --format='%h %s' | trello card comment "$branch"

# Close the card when the branch merges (in a post-merge hook)
trello card mv "$branch" --list "Done" && trello card due "$branch" --complete
```

## Webhooks

```sh
# Notify a service whenever the board changes
trello webhook create \
  --callback-url "https://example.com/trello" \
  --model "Engineering" \
  --description "board events"

trello token webhooks                 # what this token has registered
trello webhook delete <id> --yes
```

The callback URL must already answer a `HEAD` request when you register it —
Trello verifies it before accepting.

## Copying and templating

```sh
# Duplicate a card, keeping its checklists
trello card create "Sprint 12 release" --list "To Do" \
  --from-card "Sprint 11 release" --param keepFromSource=checklists,labels

# Duplicate a whole board
trello board create "Sprint 12" --from-board "Sprint template" --workspace "Acme"
trello board create "Sprint 12" --from-board "Sprint template" --keep-from-source cards
```

## Two accounts

```sh
trello --profile work auth login
trello --profile work board ls
trello --profile personal card ls --list "Someday"
trello config profiles
```

## When something is missing

Every endpoint has a command; find it rather than reaching for `curl`:

```sh
trello docs endpoints sticker
trello docs endpoints "custom field"
trello docs coverage
```

And when Trello supports a parameter the command does not declare:

```sh
trello board cards "Engineering" --param since=2026-07-01
trello api /boards/aBcD1234/cards since=2026-07-01 before=2026-08-01
```
