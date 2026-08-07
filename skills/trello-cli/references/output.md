# Shaping the output

Every command accepts the same output flags. Pick the narrowest one that gives
you what you need — it is faster to read and harder to misparse.

## Formats

| Flag | Shape | Use it when |
|---|---|---|
| *(default)* | Aligned table, coloured on a TTY | A human is reading |
| `-o json` | Trello's response, pretty-printed and unmodified | You will parse it |
| `-o jsonl` | One compact object per line | Streaming, `while read` |
| `-o yaml` | The same data, indented | Diffing, config files |
| `-o csv` / `-o tsv` | Rows | Spreadsheets, `cut`, `awk` |
| `-o id` | One id per line, nothing else | Piping into `xargs` |
| `-o plain` | Selected columns, space-separated, no header | Quick shell reads |
| `--wide` | Table with every column | Exploring |

Table output is truncated to keep columns aligned. **When stdout is a pipe,
truncation and colour are off automatically**, so `trello card ls > out.txt` is
untruncated — but it is still a table. Use `-o json` if you will parse it.

## Narrowing

```sh
# One field per object
trello card ls --list "To Do" --field name
trello board ls --field shortUrl

# A nested field, dotted
trello card show "Ship v2" --field badges.votes
trello card ls --list Done --field labels.name

# Chosen columns
trello card ls --list "To Do" --columns name,due,labels

# Your own shape
trello card ls --list "To Do" --template '{{.name}}|{{.due}}|{{.shortUrl}}'
```

Template functions available: `json`, `upper`, `lower`, `trim`, `join`, `field`.

`--field` gives you one line per object in the table-ish formats and a JSON
array in `-o json`. Objects whose field is null still get a line, so line *N*
always corresponds to object *N* and you can zip the output back against the
list you asked about.

```sh
trello card ls --list "To Do" --template '{{join ", " (field . "labels.name")}}'
```

## Asking Trello for less

`--fields` is a *server-side* filter: it changes what Trello sends, not just
what is printed. On a large board this is the difference between a 2 MB response
and a 20 kB one.

```sh
trello board cards "Engineering" --fields name,due,idList -o json
trello board cards "Engineering" --limit 50
trello board cards "Engineering" --filter open
```

`--field` (singular) narrows what you print. `--fields` (plural) narrows what is
fetched. Use both when you want one value from a large collection:

```sh
trello board cards "Engineering" --fields name --field name
```

## stdout versus stderr

Data goes to stdout. Confirmations, warnings and progress go to stderr. This is
what makes redirection safe:

```sh
trello card create "New" --list "To Do" -o json > card.json   # clean JSON
trello card create "New" --list "To Do" -q                    # silence stderr
```

## Dates

Dates print as relative times ("2h ago", "in 3d") because that is how boards are
read. For a stable, sortable format:

```sh
trello card ls --list "To Do" --time-format 2006-01-02
trello card ls --list "To Do" --time-format 2006-01-02T15:04:05Z07:00
```

Or take the raw ISO string with `-o json`, which never reformats.

## Examples

```sh
# Names of every overdue card assigned to me
trello card ls --member me --overdue --field name

# Board id for a name
trello board ls --field id | head -1

# CSV of a list, for a spreadsheet
trello card ls --list "Done" -o csv --columns name,due,labels > done.csv

# Feed ids into another command
trello card ls --list "Done" -o id | xargs -n1 trello card archive -y

# Count cards per list
trello list ls --counts
```
