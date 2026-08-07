# Command reference

Every one of the 261 Trello REST endpoints has a command. This file is generated
from `api/commands.json`; run `trello docs endpoints <filter>` for a live,
searchable version.

## Hand-written commands

These do more than call one endpoint — they resolve names, join several calls,
or reshape the output. Prefer them over the generated equivalents.

| Command | What it does |
|---|---|
| `trello auth login` | Store an API key and token |
| `trello auth status` | Check who you are signed in as (exit 3 when not) |
| `trello auth logout` | Forget the stored credentials |
| `trello auth whoami` | Print your username |
| `trello use board \"<name>\"` | Set the board later commands default to |
| `trello use list \"<name>\"` | Set the default list |
| `trello use` | Show the current defaults |
| `trello me` | Your member record |
| `trello boards` | Your boards (shorthand for `board ls`) |
| `trello board ls` | Boards, with `--all`, `--starred`, `--workspace` |
| `trello list ls [board]` | Lists on a board, with `--counts` |
| `trello card ls` | Cards, with `--list`, `--member`, `--label`, `--overdue`, `--due-soon` |
| `trello card create <name>` | Create a card, with `--list --due --label --member --attach` |
| `trello card show <card>` | One card in full, with `--comments` |
| `trello card mv <card>` | Move it, with `--list`, `--to-board`, `--position` |
| `trello card comment <card> <text>` | Add a comment, or read them with `--list` |
| `trello card assign` / `unassign` | Add or remove members |
| `trello card label` / `unlabel` | Add or remove labels |
| `trello card due <card> <when>` | Set, clear (`--clear`) or complete (`--complete`) |
| `trello card archive` / `unarchive` | Archive or restore |
| `trello card attachments download` | Write attachment files to disk, with `--all --preview --out` |
| `trello search <query>` | Search, with `--type`, `--in-board`, `--limit` |
| `trello open [name]` | Open a board or card in a browser, or print `--url` |
| `trello api <path>` | Any endpoint, authenticated |
| `trello docs endpoints [filter]` | The full endpoint-to-command map |
| `trello config show` / `set` / `profiles` | Settings |
| `trello completion <shell>` | Completion script |


## Generated commands

One per endpoint, grouped by the object they act on. `[brackets]` mark an
argument that can be omitted when `trello use` has set a default.


### Actions — `trello action`

| Command | Endpoint | Description |
|---|---|---|
| `trello action board <action>` | `GET /actions/{id}/board` | Show the board an action happened on |
| `trello action card <action>` | `GET /actions/{id}/card` | Show the card an action happened on |
| `trello action delete <action>` | `DELETE /actions/{id}` | Delete a comment for good |
| `trello action field <action> <field>` | `GET /actions/{id}/{field}` | Show one field of an action |
| `trello action get <action>` | `GET /actions/{id}` | Show a single action |
| `trello action list <action>` | `GET /actions/{id}/list` | Show the list an action happened on |
| `trello action member <action>` | `GET /actions/{id}/member` | Show the member an action is about |
| `trello action member-creator <action>` | `GET /actions/{id}/memberCreator` | Show the member who performed an action |
| `trello action reactions <action>` | `GET /actions/{idAction}/reactions` | List the reactions on an action |
| `trello action reactions add <action>` | `POST /actions/{idAction}/reactions` | React to an action |
| `trello action reactions get <action> <reaction>` | `GET /actions/{idAction}/reactions/{id}` | Show one reaction on an action |
| `trello action reactions rm <action> <reaction>` | `DELETE /actions/{idAction}/reactions/{id}` | Take a reaction off an action |
| `trello action reactions summary <action>` | `GET /actions/{idAction}/reactionsSummary` | Count the reactions on an action by emoji |
| `trello action text update <action> <value>` | `PUT /actions/{id}/text` | Set the text of a comment |
| `trello action update <action> <text>` | `PUT /actions/{id}` | Change the text of a comment |
| `trello action workspace <action>` | `GET /actions/{id}/organization` | Show the workspace an action happened in |

### Applications — `trello app`

| Command | Endpoint | Description |
|---|---|---|
| `trello app compliance <api-key>` | `GET /applications/{key}/compliance` | Show the compliance data of an app by its API key |

### Batch — `trello batch`

| Command | Endpoint | Description |
|---|---|---|
| `trello batch get <url>...` | `GET /batch` | Run up to 10 GET requests in one call |

### Boards — `trello board`

| Command | Endpoint | Description |
|---|---|---|
| `trello board actions [board]` | `GET /boards/{boardId}/actions` | Show recent activity on a board |
| `trello board calendar-key create [board]` | `POST /boards/{id}/calendarKey/generate` | Generate a new calendar feed key for a board |
| `trello board cards [board]` | `GET /boards/{id}/cards` | List the open cards on a board |
| `trello board cards filter [board] <filter>` | `GET /boards/{id}/cards/{filter}` | List the cards on a board matching a filter |
| `trello board checklists [board]` | `GET /boards/{id}/checklists` | List the checklists on a board |
| `trello board create <name>` | `POST /boards` | Create a board |
| `trello board custom-fields [board]` | `GET /boards/{id}/customFields` | List the custom fields defined on a board |
| `trello board delete [board]` | `DELETE /boards/{id}` | Delete a board permanently |
| `trello board email-key create [board]` | `POST /boards/{id}/emailKey/generate` | Generate a new email-to-board address key for a board |
| `trello board exports create [board]` | `POST /boards/{id}/exports` | Start an export of a board |
| `trello board exports delete [board] <export>` | `DELETE /boards/{id}/exports/{idExport}` | Delete a board export |
| `trello board exports download [board] <export>` | `GET /boards/{id}/exports/{idExport}/download` | Download a finished board export |
| `trello board exports get [board] <export>` | `GET /boards/{id}/exports/{idExport}` | Show the status of a board export |
| `trello board exports latest [board]` | `GET /boards/{id}/exports/mostRecent` | Show the most recent export of a board |
| `trello board field [board] <field>` | `GET /boards/{id}/{field}` | Show a single field of a board |
| `trello board get [board]` | `GET /boards/{id}` | Show a board |
| `trello board labels [board]` | `GET /boards/{id}/labels` | List the labels on a board |
| `trello board labels create [board]` | `POST /boards/{id}/labels` | Create a label on a board |
| `trello board lists [board]` | `GET /boards/{id}/lists` | List the lists on a board |
| `trello board lists add [board] <name>` | `POST /boards/{id}/lists` | Create a list on a board |
| `trello board lists filter [board] <filter>` | `GET /boards/{id}/lists/{filter}` | List the lists on a board matching a filter |
| `trello board mark-viewed [board]` | `POST /boards/{id}/markedAsViewed` | Mark a board as viewed |
| `trello board members [board]` | `GET /boards/{id}/members` | List the members of a board |
| `trello board members add [board] <member>` | `PUT /boards/{id}/members/{idMember}` | Add a member to a board |
| `trello board members invite [board] <email>` | `PUT /boards/{id}/members` | Invite someone to a board by email |
| `trello board members rm [board] <member>` | `DELETE /boards/{id}/members/{idMember}` | Remove a member from a board |
| `trello board memberships [board]` | `GET /boards/{id}/memberships` | List the memberships on a board |
| `trello board memberships update [board] <membership>` | `PUT /boards/{id}/memberships/{idMembership}` | Change a member's role on a board |
| `trello board powerups [board]` | `GET /boards/{id}/boardPlugins` | List the Power-Ups enabled on a board |
| `trello board powerups available [board]` | `GET /boards/{id}/plugins` | List the Power-Ups on a board |
| `trello board powerups disable [board] <plugin>` | `DELETE /boards/{id}/boardPlugins/{idPlugin}` | Disable a Power-Up on a board |
| `trello board powerups enable [board] <plugin>` | `POST /boards/{id}/boardPlugins` | Enable a Power-Up on a board |
| `trello board prefs email-list update [board] [value]` | `PUT /boards/{id}/myPrefs/idEmailList` | Set the list that cards created by email land in |
| `trello board prefs email-position update [board] <value>` | `PUT /boards/{id}/myPrefs/emailPosition` | Set where cards created by email are added |
| `trello board prefs show-sidebar update [board] <value>` | `PUT /boards/{id}/myPrefs/showSidebar` | Show or hide the sidebar on a board |
| `trello board prefs show-sidebar-activity update [board] <value>` | `PUT /boards/{id}/myPrefs/showSidebarActivity` | Show or hide activity in a board's sidebar |
| `trello board prefs show-sidebar-board-actions update [board] <value>` | `PUT /boards/{id}/myPrefs/showSidebarBoardActions` | Show or hide board actions in a board's sidebar |
| `trello board prefs show-sidebar-members update [board] <value>` | `PUT /boards/{id}/myPrefs/showSidebarMembers` | Show or hide members in a board's sidebar |
| `trello board stars [board]` | `GET /boards/{boardId}/boardStars` | List the stars on a board |
| `trello board tags add [board] <value>` | `POST /boards/{id}/idTags` | Add a workspace tag to a board |
| `trello board update [board]` | `PUT /boards/{id}` | Update a board's name, description or preferences |

### Cards — `trello card`

| Command | Endpoint | Description |
|---|---|---|
| `trello card actions [card]` | `GET /cards/{id}/actions` | List the activity on a card |
| `trello card attachments [card]` | `GET /cards/{id}/attachments` | List the attachments on a card |
| `trello card attachments add [card]` | `POST /cards/{id}/attachments` | Attach a file or link to a card |
| `trello card attachments delete [card] <attachment>` | `DELETE /cards/{id}/attachments/{idAttachment}` | Remove an attachment from a card |
| `trello card attachments get [card] <attachment>` | `GET /cards/{id}/attachments/{idAttachment}` | Show one attachment on a card |
| `trello card attachments download [card] [attachment]` | — (fetches the attachment URL) | Write attachment files to disk so they can be opened |
| `trello card board [card]` | `GET /cards/{id}/board` | Show the board a card belongs to |
| `trello card check-items [card]` | `GET /cards/{id}/checkItemStates` | Show which check items on a card are done |
| `trello card check-items delete [card] <check-item>` | `DELETE /cards/{id}/checkItem/{idCheckItem}` | Delete a check item from a card |
| `trello card check-items get [card] <check-item>` | `GET /cards/{id}/checkItem/{idCheckItem}` | Show one check item on a card |
| `trello card check-items update [card] <check-item>` | `PUT /cards/{id}/checkItem/{idCheckItem}` | Tick off or edit a check item on a card |
| `trello card checklists [card]` | `GET /cards/{id}/checklists` | List the checklists on a card |
| `trello card checklists add [card] [name]` | `POST /cards/{id}/checklists` | Add a checklist to a card |
| `trello card checklists check-items update [card] <checklist> <check-item>` | `PUT /cards/{idCard}/checklist/{idChecklist}/checkItem/{idCheckItem}` | Move a check item within its checklist on a card |
| `trello card checklists delete [card] <checklist>` | `DELETE /cards/{id}/checklists/{idChecklist}` | Delete a checklist from a card |
| `trello card comments add [card] <text>` | `POST /cards/{id}/actions/comments` | Comment on a card |
| `trello card comments delete [card] <action>` | `DELETE /cards/{id}/actions/{idAction}/comments` | Delete a comment from a card |
| `trello card comments update [card] <action> <text>` | `PUT /cards/{id}/actions/{idAction}/comments` | Edit a comment on a card |
| `trello card create [name]` | `POST /cards` | Create a card |
| `trello card custom-fields [card]` | `GET /cards/{id}/customFieldItems` | Show the custom field values on a card |
| `trello card custom-fields update [card] <custom-field>` | `PUT /cards/{idCard}/customField/{idCustomField}/item` | Set the value of one custom field on a card |
| `trello card custom-fields update-many [card]` | `PUT /cards/{idCard}/customFields` | Set several custom field values on a card at once |
| `trello card delete [card]` | `DELETE /cards/{id}` | Delete a card for good |
| `trello card field [card] <field>` | `GET /cards/{id}/{field}` | Show a single field of a card |
| `trello card get [card]` | `GET /cards/{id}` | Show a card |
| `trello card labels add [card] <value>` | `POST /cards/{id}/idLabels` | Put an existing label on a card |
| `trello card labels create [card] [name]` | `POST /cards/{id}/labels` | Create a new board label and put it on a card |
| `trello card labels rm [card] <label>` | `DELETE /cards/{id}/idLabels/{idLabel}` | Take a label off a card |
| `trello card list [card]` | `GET /cards/{id}/list` | Show the list a card sits in |
| `trello card members [card]` | `GET /cards/{id}/members` | List the members assigned to a card |
| `trello card members add [card] <value>` | `POST /cards/{id}/idMembers` | Put a member on a card |
| `trello card members rm [card] <member>` | `DELETE /cards/{id}/idMembers/{idMember}` | Take a member off a card |
| `trello card notifications read [card]` | `POST /cards/{id}/markAssociatedNotificationsRead` | Mark this card's notifications as read |
| `trello card plugin-data [card]` | `GET /cards/{id}/pluginData` | Show power-up data stored on a card |
| `trello card stickers [card]` | `GET /cards/{id}/stickers` | List the stickers on a card |
| `trello card stickers add [card] <sticker>` | `POST /cards/{id}/stickers` | Put a sticker on a card |
| `trello card stickers get [card] <sticker>` | `GET /cards/{id}/stickers/{idSticker}` | Show one sticker on a card |
| `trello card stickers rm [card] <sticker>` | `DELETE /cards/{id}/stickers/{idSticker}` | Remove a sticker from a card |
| `trello card stickers update [card] <sticker>` | `PUT /cards/{id}/stickers/{idSticker}` | Move or rotate a sticker on a card |
| `trello card update [card]` | `PUT /cards/{id}` | Change a card's fields |
| `trello card votes [card]` | `GET /cards/{id}/membersVoted` | List the members who voted for a card |
| `trello card votes add [card] [value]` | `POST /cards/{id}/membersVoted` | Vote for a card |
| `trello card votes rm [card] [member]` | `DELETE /cards/{id}/membersVoted/{idMember}` | Take back a vote on a card |

### Checklists — `trello checklist`

| Command | Endpoint | Description |
|---|---|---|
| `trello checklist board <checklist>` | `GET /checklists/{id}/board` | Show the board a checklist belongs to |
| `trello checklist card <checklist>` | `GET /checklists/{id}/cards` | Show the card a checklist is on |
| `trello checklist check-items <checklist>` | `GET /checklists/{id}/checkItems` | List the items on a checklist |
| `trello checklist check-items add <checklist> <name>` | `POST /checklists/{id}/checkItems` | Add an item to a checklist |
| `trello checklist check-items delete <checklist> <check-item>` | `DELETE /checklists/{id}/checkItems/{idCheckItem}` | Remove an item from a checklist |
| `trello checklist check-items get <checklist> <check-item>` | `GET /checklists/{id}/checkItems/{idCheckItem}` | Show one item on a checklist |
| `trello checklist create [name]` | `POST /checklists` | Create a checklist on a card |
| `trello checklist delete <checklist>` | `DELETE /checklists/{id}` | Delete a checklist and every item on it |
| `trello checklist field <checklist> <field>` | `GET /checklists/{id}/{field}` | Show one field of a checklist |
| `trello checklist field update <checklist> <field> <value>` | `PUT /checklists/{id}/{field}` | Set one field on a checklist |
| `trello checklist get <checklist>` | `GET /checklists/{id}` | Show a checklist and its items |
| `trello checklist update <checklist>` | `PUT /checklists/{id}` | Rename a checklist or move it up or down the card |

### Custom Fields — `trello customfield`

| Command | Endpoint | Description |
|---|---|---|
| `trello customfield create <name>` | `POST /customFields` | Create a custom field on a board |
| `trello customfield delete <custom-field>` | `DELETE /customFields/{id}` | Delete a custom field from a board |
| `trello customfield get <custom-field>` | `GET /customFields/{id}` | Show a custom field |
| `trello customfield options <custom-field>` | `GET /customFields/{id}/options` | List the options of a dropdown custom field |
| `trello customfield options add <custom-field>` | `POST /customFields/{id}/options` | Add an option to a dropdown custom field |
| `trello customfield options delete <custom-field> <option>` | `DELETE /customFields/{id}/options/{idCustomFieldOption}` | Remove an option from a dropdown custom field |
| `trello customfield options get <custom-field> <option>` | `GET /customFields/{id}/options/{idCustomFieldOption}` | Show one option of a dropdown custom field |
| `trello customfield update <custom-field>` | `PUT /customFields/{id}` | Rename or reposition a custom field |

### Emoji — `trello emoji`

| Command | Endpoint | Description |
|---|---|---|
| `trello emoji ls` | `GET /emoji` | List the emoji Trello knows about |

### Enterprises — `trello enterprise`

| Command | Endpoint | Description |
|---|---|---|
| `trello enterprise admins <enterprise>` | `GET /enterprises/{id}/admins` | List the admins of an enterprise |
| `trello enterprise admins add <enterprise> [member]` | `PUT /enterprises/{id}/admins/{idMember}` | Make a member an admin of an enterprise |
| `trello enterprise admins rm <enterprise> [member]` | `DELETE /enterprises/{id}/admins/{idMember}` | Remove a member as an admin of an enterprise |
| `trello enterprise audit-log <enterprise>` | `GET /enterprises/{id}/auditlog` | Show the audit log of an enterprise |
| `trello enterprise get <enterprise>` | `GET /enterprises/{id}` | Show an enterprise |
| `trello enterprise join-requests decline <enterprise> <workspace>...` | `PUT /enterprises/{id}/enterpriseJoinRequest/bulk` | Decline workspace requests to join an enterprise |
| `trello enterprise members <enterprise>` | `GET /enterprises/{id}/members` | List the members of an enterprise |
| `trello enterprise members deactivate <enterprise> [member]` | `PUT /enterprises/{id}/members/{idMember}/deactivated` | Deactivate or reactivate a member of an enterprise |
| `trello enterprise members get <enterprise> [member]` | `GET /enterprises/{id}/members/{idMember}` | Show one member of an enterprise |
| `trello enterprise members license <enterprise> [member]` | `PUT /enterprises/{id}/members/{idMember}/licensed` | Grant or revoke a member's enterprise license |
| `trello enterprise members search <enterprise>` | `GET /enterprises/{id}/members/query` | Search the users of an enterprise |
| `trello enterprise signup-url <enterprise>` | `GET /enterprises/{id}/signupUrl` | Get the signup URL for an enterprise |
| `trello enterprise tokens create <enterprise>` | `POST /enterprises/{id}/tokens` | Create an auth token for an enterprise |
| `trello enterprise workspaces <enterprise>` | `GET /enterprises/{id}/organizations` | List the workspaces in an enterprise |
| `trello enterprise workspaces accept <enterprise> <workspace>...` | `GET /enterprises/{id}/organizations/bulk/{idOrganizations}` | Accept several workspaces into an enterprise at once |
| `trello enterprise workspaces add <enterprise> [workspace]` | `PUT /enterprises/{id}/organizations` | Transfer a workspace into an enterprise |
| `trello enterprise workspaces claimable <enterprise>` | `GET /enterprises/{id}/claimableOrganizations` | List the workspaces an enterprise can claim |
| `trello enterprise workspaces pending <enterprise>` | `GET /enterprises/{id}/pendingOrganizations` | List the workspaces waiting to join an enterprise |
| `trello enterprise workspaces rm <enterprise> [workspace]` | `DELETE /enterprises/{id}/organizations/{idOrg}` | Remove a workspace from an enterprise |
| `trello enterprise workspaces transferrable <enterprise> [workspace]` | `GET /enterprises/{id}/transferrable/organization/{idOrganization}` | Check whether a workspace can be transferred to an enterprise |
| `trello enterprise workspaces transferrable bulk <enterprise> <workspace>...` | `GET /enterprises/{id}/transferrable/bulk/{idOrganizations}` | Check which of several workspaces can be transferred to an enterprise |

### Labels — `trello label`

| Command | Endpoint | Description |
|---|---|---|
| `trello label create <name>` | `POST /labels` | Create a label on a board |
| `trello label delete <label>` | `DELETE /labels/{id}` | Delete a label from the board and from every card using it |
| `trello label field update <label> <field> <value>` | `PUT /labels/{id}/{field}` | Set one field on a label |
| `trello label get <label>` | `GET /labels/{id}` | Show a label |
| `trello label update <label>` | `PUT /labels/{id}` | Rename a label or change its color |

### Lists — `trello list`

| Command | Endpoint | Description |
|---|---|---|
| `trello list actions [list]` | `GET /lists/{id}/actions` | Show recent activity on a list |
| `trello list archive [list]` | `PUT /lists/{id}/closed` | Archive or unarchive a list |
| `trello list board [list]` | `GET /lists/{id}/board` | Show the board a list belongs to |
| `trello list cards [list]` | `GET /lists/{id}/cards` | List the cards in a list |
| `trello list cards archive [list]` | `POST /lists/{id}/archiveAllCards` | Archive every card in a list |
| `trello list cards move [list]` | `POST /lists/{id}/moveAllCards` | Move every card in a list to another list |
| `trello list create <name>` | `POST /lists` | Create a list on a board |
| `trello list field update [list] <field> [value]` | `PUT /lists/{id}/{field}` | Set one field on a list |
| `trello list get [list]` | `GET /lists/{id}` | Show a list |
| `trello list move [list]` | `PUT /lists/{id}/idBoard` | Move a list to another board |
| `trello list update [list]` | `PUT /lists/{id}` | Rename a list or change its position, board or subscription |

### Members — `trello member`

| Command | Endpoint | Description |
|---|---|---|
| `trello member actions [member]` | `GET /members/{id}/actions` | List a member's recent activity |
| `trello member avatar upload [member]` | `POST /members/{id}/avatar` | Upload a new avatar for a member |
| `trello member board-backgrounds [member]` | `GET /members/{id}/boardBackgrounds` | List a member's board backgrounds |
| `trello member board-backgrounds delete [member] <background>` | `DELETE /members/{id}/boardBackgrounds/{idBackground}` | Delete a board background |
| `trello member board-backgrounds get [member] <background>` | `GET /members/{id}/boardBackgrounds/{idBackground}` | Show one of a member's board backgrounds |
| `trello member board-backgrounds update [member] <background>` | `PUT /members/{id}/boardBackgrounds/{idBackground}` | Update a board background |
| `trello member board-backgrounds upload [member]` | `POST /members/{id}/boardBackgrounds` | Upload a new board background |
| `trello member board-stars [member]` | `GET /members/{id}/boardStars` | List the boards a member has starred |
| `trello member board-stars add [member]` | `POST /members/{id}/boardStars` | Star a board for a member |
| `trello member board-stars get [member] <star>` | `GET /members/{id}/boardStars/{idStar}` | Show one of a member's starred boards |
| `trello member board-stars rm [member] <star>` | `DELETE /members/{id}/boardStars/{idStar}` | Unstar a board |
| `trello member board-stars update [member] <star>` | `PUT /members/{id}/boardStars/{idStar}` | Change the position of a starred board |
| `trello member boards [member]` | `GET /members/{id}/boards` | List the boards a member belongs to |
| `trello member boards-invited [member]` | `GET /members/{id}/boardsInvited` | List the boards a member has been invited to |
| `trello member cards [member]` | `GET /members/{id}/cards` | List the cards a member is on |
| `trello member custom-board-backgrounds [member]` | `GET /members/{id}/customBoardBackgrounds` | List a member's custom board backgrounds |
| `trello member custom-board-backgrounds delete [member] <background>` | `DELETE /members/{id}/customBoardBackgrounds/{idBackground}` | Delete a custom board background |
| `trello member custom-board-backgrounds get [member] <background>` | `GET /members/{id}/customBoardBackgrounds/{idBackground}` | Show one custom board background |
| `trello member custom-board-backgrounds update [member] <background>` | `PUT /members/{id}/customBoardBackgrounds/{idBackground}` | Update a custom board background |
| `trello member custom-board-backgrounds upload [member]` | `POST /members/{id}/customBoardBackgrounds` | Upload a custom board background |
| `trello member custom-emoji [member]` | `GET /members/{id}/customEmoji` | List a member's custom emoji |
| `trello member custom-emoji get [member] <emoji>` | `GET /members/{id}/customEmoji/{idEmoji}` | Show one of a member's custom emoji |
| `trello member custom-emoji upload [member]` | `POST /members/{id}/customEmoji` | Upload a new custom emoji |
| `trello member custom-stickers [member]` | `GET /members/{id}/customStickers` | List a member's custom stickers |
| `trello member custom-stickers delete [member] <sticker>` | `DELETE /members/{id}/customStickers/{idSticker}` | Delete a custom sticker |
| `trello member custom-stickers get [member] <sticker>` | `GET /members/{id}/customStickers/{idSticker}` | Show one of a member's custom stickers |
| `trello member custom-stickers upload [member]` | `POST /members/{id}/customStickers` | Upload a new custom sticker |
| `trello member field [member] <field>` | `GET /members/{id}/{field}` | Show a single field of a member |
| `trello member get [member]` | `GET /members/{id}` | Show a member's profile |
| `trello member messages dismiss [member]` | `POST /members/{id}/oneTimeMessagesDismissed` | Dismiss a one-time message for a member |
| `trello member notification-settings [member]` | `GET /members/{id}/notificationsChannelSettings` | Show a member's notification channel settings |
| `trello member notification-settings blocked-keys [member] <channel>` | `GET /members/{id}/notificationsChannelSettings/{channel}` | List the notification keys blocked on a channel |
| `trello member notification-settings blocked-keys block [member] <channel> <blocked-keys>` | `PUT /members/{id}/notificationsChannelSettings/{channel}/{blockedKeys}` | Block a single notification key on a channel |
| `trello member notification-settings blocked-keys update [member] <channel>` | `PUT /members/{id}/notificationsChannelSettings/{channel}` | Replace the notification keys blocked on a channel |
| `trello member notification-settings update [member]` | `PUT /members/{id}/notificationsChannelSettings` | Set which notifications are blocked on a channel |
| `trello member notifications [member]` | `GET /members/{id}/notifications` | List a member's notifications |
| `trello member saved-searches [member]` | `GET /members/{id}/savedSearches` | List a member's saved searches |
| `trello member saved-searches create [member]` | `POST /members/{id}/savedSearches` | Create a saved search |
| `trello member saved-searches delete [member] <search>` | `DELETE /members/{id}/savedSearches/{idSearch}` | Delete a saved search |
| `trello member saved-searches get [member] <search>` | `GET /members/{id}/savedSearches/{idSearch}` | Show a saved search |
| `trello member saved-searches update [member] <search>` | `PUT /members/{id}/savedSearches/{idSearch}` | Update a saved search |
| `trello member tokens [member]` | `GET /members/{id}/tokens` | List the app tokens a member has issued |
| `trello member update [member]` | `PUT /members/{id}` | Update a member's profile |
| `trello member workspaces [member]` | `GET /members/{id}/organizations` | List the workspaces a member belongs to |
| `trello member workspaces-invited [member]` | `GET /members/{id}/organizationsInvited` | List the workspaces a member has been invited to |

### Notifications — `trello notification`

| Command | Endpoint | Description |
|---|---|---|
| `trello notification board <notification>` | `GET /notifications/{id}/board` | Show the board a notification is about |
| `trello notification card <notification>` | `GET /notifications/{id}/card` | Show the card a notification is about |
| `trello notification field <notification> <field>` | `GET /notifications/{id}/{field}` | Show one field of a notification |
| `trello notification get <notification>` | `GET /notifications/{id}` | Show a single notification |
| `trello notification list <notification>` | `GET /notifications/{id}/list` | Show the list a notification is about |
| `trello notification member <notification>` | `GET /notifications/{id}/member` | Show the member a notification is about |
| `trello notification member-creator <notification>` | `GET /notifications/{id}/memberCreator` | Show the member who triggered a notification |
| `trello notification read <notification>` | `PUT /notifications/{id}` | Mark a notification as read |
| `trello notification read-all` | `POST /notifications/all/read` | Mark every notification as read |
| `trello notification unread <notification>` | `PUT /notifications/{id}/unread` | Mark a notification as unread |
| `trello notification workspace <notification>` | `GET /notifications/{id}/organization` | Show the workspace a notification is about |

### Power-Ups — `trello powerup`

| Command | Endpoint | Description |
|---|---|---|
| `trello powerup compliance <plugin>` | `GET /plugins/{id}/compliance/memberPrivacy` | Show whether a Power-Up stores member data |
| `trello powerup get <plugin>` | `GET /plugins/{id}` | Show a Power-Up |
| `trello powerup listings add <plugin>` | `POST /plugins/{idPlugin}/listing` | Add a localized listing to a Power-Up |
| `trello powerup listings update <plugin> <listing>` | `PUT /plugins/{idPlugin}/listings/{idListing}` | Update a Power-Up's listing |
| `trello powerup update <plugin>` | `PUT /plugins/{id}` | Update a Power-Up you own |

### Search — `trello search`

| Command | Endpoint | Description |
|---|---|---|
| `trello search all <query>` | `GET /search` | Search boards, cards, members and workspaces |
| `trello search members <query>` | `GET /search/members` | Search for Trello members by name or username |

### Tokens — `trello token`

| Command | Endpoint | Description |
|---|---|---|
| `trello token delete <token>` | `DELETE /tokens/{token}` | Revoke an API token |
| `trello token get <token>` | `GET /tokens/{token}` | Show details of an API token |
| `trello token member <token>` | `GET /tokens/{token}/member` | Show the member a token belongs to |
| `trello token webhooks <token>` | `GET /tokens/{token}/webhooks` | List the webhooks created with a token |
| `trello token webhooks add <token>` | `POST /tokens/{token}/webhooks` | Create a webhook under a token |
| `trello token webhooks delete <token> <webhook>` | `DELETE /tokens/{token}/webhooks/{idWebhook}` | Delete a webhook created with a token |
| `trello token webhooks get <token> <webhook>` | `GET /tokens/{token}/webhooks/{idWebhook}` | Show one webhook created with a token |
| `trello token webhooks update <token> <webhook>` | `PUT /tokens/{token}/webhooks/{idWebhook}` | Update a webhook created with a token |

### Webhooks — `trello webhook`

| Command | Endpoint | Description |
|---|---|---|
| `trello webhook create` | `POST /webhooks` | Create a webhook that watches a board, list or card |
| `trello webhook delete <webhook>` | `DELETE /webhooks/{id}` | Delete a webhook |
| `trello webhook field <webhook> <field>` | `GET /webhooks/{id}/{field}` | Show a single field of a webhook |
| `trello webhook get <webhook>` | `GET /webhooks/{id}` | Show a webhook |
| `trello webhook update <webhook>` | `PUT /webhooks/{id}` | Change a webhook's callback URL, target or active flag |

### Workspaces — `trello workspace`

| Command | Endpoint | Description |
|---|---|---|
| `trello workspace actions [workspace]` | `GET /organizations/{id}/actions` | Show recent activity in a workspace |
| `trello workspace boards [workspace]` | `GET /organizations/{id}/boards` | List the boards in a workspace |
| `trello workspace create <display-name>` | `POST /organizations` | Create a workspace |
| `trello workspace delete [workspace]` | `DELETE /organizations/{id}` | Delete a workspace for good |
| `trello workspace exports [workspace]` | `GET /organizations/{id}/exports` | List the CSV exports of a workspace |
| `trello workspace exports create [workspace]` | `POST /organizations/{id}/exports` | Start a CSV export of a workspace |
| `trello workspace field [workspace] <field>` | `GET /organizations/{id}/{field}` | Show a single field of a workspace |
| `trello workspace get [workspace]` | `GET /organizations/{id}` | Show a workspace |
| `trello workspace logo rm [workspace]` | `DELETE /organizations/{id}/logo` | Remove the logo image from a workspace |
| `trello workspace logo upload [workspace]` | `POST /organizations/{id}/logo` | Set the logo image of a workspace |
| `trello workspace members [workspace]` | `GET /organizations/{id}/members` | List the members of a workspace |
| `trello workspace members add [workspace] <member>` | `PUT /organizations/{id}/members/{idMember}` | Add a member to a workspace or change their role |
| `trello workspace members deactivate [workspace] <member>` | `PUT /organizations/{id}/members/{idMember}/deactivated` | Deactivate a member of a workspace |
| `trello workspace members invite [workspace]` | `PUT /organizations/{id}/members` | Invite someone to a workspace by email |
| `trello workspace members rm [workspace] <member>` | `DELETE /organizations/{id}/members/{idMember}` | Remove a member from a workspace |
| `trello workspace members rm-all-boards [workspace] <member>` | `DELETE /organizations/{id}/members/{idMember}/all` | Remove a member from a workspace and from all its boards |
| `trello workspace memberships [workspace]` | `GET /organizations/{id}/memberships` | List the memberships of a workspace |
| `trello workspace memberships get [workspace] <membership>` | `GET /organizations/{id}/memberships/{idMembership}` | Show a single membership of a workspace |
| `trello workspace new-billable-guests [workspace] [board]` | `GET /organizations/{id}/newBillableGuests/{idBoard}` | Check whether a board adds new billable guests to a workspace |
| `trello workspace plugin-data [workspace]` | `GET /organizations/{id}/pluginData` | Show the power-up data stored on a workspace |
| `trello workspace prefs associated-domain rm [workspace]` | `DELETE /organizations/{id}/prefs/associatedDomain` | Unlink the Google Apps domain from a workspace |
| `trello workspace prefs invite-restrict rm [workspace]` | `DELETE /organizations/{id}/prefs/orgInviteRestrict` | Drop the email domain restriction on workspace invites |
| `trello workspace tags [workspace]` | `GET /organizations/{id}/tags` | List the collections in a workspace |
| `trello workspace tags create [workspace]` | `POST /organizations/{id}/tags` | Create a collection in a workspace |
| `trello workspace tags delete [workspace] <tag>` | `DELETE /organizations/{id}/tags/{idTag}` | Delete a collection from a workspace |
| `trello workspace update [workspace]` | `PUT /organizations/{id}` | Change a workspace's name, description or preferences |
