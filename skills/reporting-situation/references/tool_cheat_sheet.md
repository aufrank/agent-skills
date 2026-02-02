# MCP Tool Cheat Sheet

Generated from cached tool definitions. Use these examples to call tools via `mcpc`.

## @google

### `auth.clear`
> Clears the authentication credentials, forcing a re-login on the next request....

```bash
mcpc @google tools-call auth.clear 
```

---
### `auth.refreshToken`
> Manually triggers the token refresh process....

```bash
mcpc @google tools-call auth.refreshToken 
```

---
### `docs.create`
> Creates a new Google Doc. Can be blank or with Markdown content....

```bash
mcpc @google tools-call docs.create title:="<val>"
```
**Arguments:**
- `title` **(Required)** `string`: The title for the new Google Doc.
- `folderName` (Optional) `string`: The name of the folder to create the document in.
- `markdown` (Optional) `string`: The Markdown content to create the document from.

---
### `docs.insertText`
> Inserts text at the beginning of a Google Doc....

```bash
mcpc @google tools-call docs.insertText documentId:="<val>" text:="<val>"
```
**Arguments:**
- `documentId` **(Required)** `string`: The ID of the document to modify.
- `text` **(Required)** `string`: The text to insert at the beginning of the document.
- `tabId` (Optional) `string`: The ID of the tab to modify. If not provided, modifies the first tab.

---
### `docs.find`
> Finds Google Docs by searching for a query in their title. Supports pagination....

```bash
mcpc @google tools-call docs.find query:="<val>"
```
**Arguments:**
- `query` **(Required)** `string`: The text to search for in the document titles.
- `pageToken` (Optional) `string`: The token for the next page of results.
- `pageSize` (Optional) `number`: The maximum number of results to return.

---
### `drive.findFolder`
> Finds a folder by name in Google Drive....

```bash
mcpc @google tools-call drive.findFolder folderName:="<val>"
```
**Arguments:**
- `folderName` **(Required)** `string`: The name of the folder to find.

---
### `drive.createFolder`
> Creates a new folder in Google Drive....

```bash
mcpc @google tools-call drive.createFolder name:="<val>"
```
**Arguments:**
- `name` **(Required)** `string`: The name of the new folder.
- `parentId` (Optional) `string`: The ID of the parent folder. If not provided, creates in the root directory.

---
### `docs.move`
> Moves a document to a specified folder....

```bash
mcpc @google tools-call docs.move documentId:="<val>" folderName:="<val>"
```
**Arguments:**
- `documentId` **(Required)** `string`: The ID of the document to move.
- `folderName` **(Required)** `string`: The name of the destination folder.

---
### `docs.getText`
> Retrieves the text content of a Google Doc....

```bash
mcpc @google tools-call docs.getText documentId:="<val>"
```
**Arguments:**
- `documentId` **(Required)** `string`: The ID of the document to read.
- `tabId` (Optional) `string`: The ID of the tab to read. If not provided, returns all tabs.
- `format` (Optional) `string`: The format of the returned text (default: text).

---
### `docs.appendText`
> Appends text to the end of a Google Doc....

```bash
mcpc @google tools-call docs.appendText documentId:="<val>" text:="<val>"
```
**Arguments:**
- `documentId` **(Required)** `string`: The ID of the document to modify.
- `text` **(Required)** `string`: The text to append to the document.
- `tabId` (Optional) `string`: The ID of the tab to modify. If not provided, modifies the first tab.

---
### `docs.replaceText`
> Replaces all occurrences of a given text with new text in a Google Doc....

```bash
mcpc @google tools-call docs.replaceText documentId:="<val>" findText:="<val>" replaceText:="<val>"
```
**Arguments:**
- `documentId` **(Required)** `string`: The ID of the document to modify.
- `findText` **(Required)** `string`: The text to find in the document.
- `replaceText` **(Required)** `string`: The text to replace the found text with.
- `tabId` (Optional) `string`: The ID of the tab to modify. If not provided, replaces in all tabs (legacy behavior).

---
### `docs.listComments`
> Lists comments on a Google Doc....

```bash
mcpc @google tools-call docs.listComments documentId:="<val>"
```
**Arguments:**
- `documentId` **(Required)** `string`: The ID of the document.
- `pageSize` (Optional) `number`: Max number of comments to return.
- `includeResolved` (Optional) `boolean`: Whether to include resolved comments.
- `pageToken` (Optional) `string`: The token for the next page of results.

---
### `docs.extractIdFromUrl`
> Extracts the document ID from a Google Workspace URL....

```bash
mcpc @google tools-call docs.extractIdFromUrl url:="<val>"
```
**Arguments:**
- `url` **(Required)** `string`: The URL of the Google Workspace document.

---
### `slides.getText`
> Retrieves the text content of a Google Slides presentation....

```bash
mcpc @google tools-call slides.getText presentationId:="<val>"
```
**Arguments:**
- `presentationId` **(Required)** `string`: The ID or URL of the presentation to read.

---
### `slides.find`
> Finds Google Slides presentations by searching for a query. Supports pagination....

```bash
mcpc @google tools-call slides.find query:="<val>"
```
**Arguments:**
- `query` **(Required)** `string`: The text to search for in presentations.
- `pageToken` (Optional) `string`: The token for the next page of results.
- `pageSize` (Optional) `number`: The maximum number of results to return.

---
### `slides.getMetadata`
> Gets metadata about a Google Slides presentation....

```bash
mcpc @google tools-call slides.getMetadata presentationId:="<val>"
```
**Arguments:**
- `presentationId` **(Required)** `string`: The ID or URL of the presentation.

---
### `slides.listComments`
> Lists comments on a Google Slides presentation....

```bash
mcpc @google tools-call slides.listComments presentationId:="<val>"
```
**Arguments:**
- `presentationId` **(Required)** `string`: The ID of the presentation.
- `pageSize` (Optional) `number`: Max number of comments to return.
- `includeResolved` (Optional) `boolean`: Whether to include resolved comments.
- `pageToken` (Optional) `string`: The token for the next page of results.

---
### `sheets.getText`
> Retrieves the content of a Google Sheets spreadsheet....

```bash
mcpc @google tools-call sheets.getText spreadsheetId:="<val>"
```
**Arguments:**
- `spreadsheetId` **(Required)** `string`: The ID or URL of the spreadsheet to read.
- `format` (Optional) `string`: Output format (default: text).

---
### `sheets.getRange`
> Gets values from a specific range in a Google Sheets spreadsheet....

```bash
mcpc @google tools-call sheets.getRange spreadsheetId:="<val>" range:="<val>"
```
**Arguments:**
- `spreadsheetId` **(Required)** `string`: The ID or URL of the spreadsheet.
- `range` **(Required)** `string`: The A1 notation range to get (e.g., "Sheet1!A1:B10").

---
### `sheets.find`
> Finds Google Sheets spreadsheets by searching for a query. Supports pagination....

```bash
mcpc @google tools-call sheets.find query:="<val>"
```
**Arguments:**
- `query` **(Required)** `string`: The text to search for in spreadsheets.
- `pageToken` (Optional) `string`: The token for the next page of results.
- `pageSize` (Optional) `number`: The maximum number of results to return.

---
### `sheets.getMetadata`
> Gets metadata about a Google Sheets spreadsheet....

```bash
mcpc @google tools-call sheets.getMetadata spreadsheetId:="<val>"
```
**Arguments:**
- `spreadsheetId` **(Required)** `string`: The ID or URL of the spreadsheet.

---
### `sheets.listComments`
> Lists comments on a Google Sheet....

```bash
mcpc @google tools-call sheets.listComments spreadsheetId:="<val>"
```
**Arguments:**
- `spreadsheetId` **(Required)** `string`: The ID of the spreadsheet.
- `pageSize` (Optional) `number`: Max number of comments to return.
- `includeResolved` (Optional) `boolean`: Whether to include resolved comments.
- `pageToken` (Optional) `string`: The token for the next page of results.

---
### `drive.search`
> Searches for files and folders in Google Drive. The query can be a simple search term, a Google Drive URL, or a full query string. For more information on query strings see: https://developers.google....

```bash
mcpc @google tools-call drive.search 
```
**Arguments:**
- `query` (Optional) `string`: A simple search term (e.g., "Budget Q3"), a Google Drive URL, or a full query string (e.g., "name contains 'Budget' and owners in 'user@example.com'" ).
- `pageSize` (Optional) `number`: The maximum number of results to return.
- `pageToken` (Optional) `string`: The token for the next page of results.
- `corpus` (Optional) `string`: The corpus of files to search (e.g., "user", "domain").
- `unreadOnly` (Optional) `boolean`: Whether to filter for unread files only.
- `sharedWithMe` (Optional) `boolean`: Whether to search for files shared with the user.

---
### `drive.downloadFile`
> Downloads the content of a file from Google Drive to a local path. Note: Google Docs, Sheets, and Slides require specialized handling....

```bash
mcpc @google tools-call drive.downloadFile fileId:="<val>" localPath:="<val>"
```
**Arguments:**
- `fileId` **(Required)** `string`: The ID of the file to download.
- `localPath` **(Required)** `string`: The local file path where the content should be saved (e.g., "downloads/report.pdf").

---
### `calendar.list`
> Lists all of the user's calendars....

```bash
mcpc @google tools-call calendar.list 
```

---
### `calendar.createEvent`
> Creates a new event in a calendar....

```bash
mcpc @google tools-call calendar.createEvent calendarId:="<val>" summary:="<val>" start:="<val>" end:="<val>"
```
**Arguments:**
- `calendarId` **(Required)** `string`: The ID of the calendar to create the event in.
- `summary` **(Required)** `string`: The summary or title of the event.
- `description` (Optional) `string`: The description of the event.
- `start` **(Required)** `object`: 
- `end` **(Required)** `object`: 
- `attendees` (Optional) `array`: The email addresses of the attendees.

---
### `calendar.listEvents`
> Lists events from a calendar. Defaults to upcoming events....

```bash
mcpc @google tools-call calendar.listEvents calendarId:="<val>"
```
**Arguments:**
- `calendarId` **(Required)** `string`: The ID of the calendar to list events from.
- `timeMin` (Optional) `string`: The start time for the event search. Defaults to the current time.
- `timeMax` (Optional) `string`: The end time for the event search.
- `attendeeResponseStatus` (Optional) `array`: The response status of the attendee.

---
### `calendar.getEvent`
> Gets the details of a specific calendar event....

```bash
mcpc @google tools-call calendar.getEvent eventId:="<val>"
```
**Arguments:**
- `eventId` **(Required)** `string`: The ID of the event to retrieve.
- `calendarId` (Optional) `string`: The ID of the calendar the event belongs to. Defaults to the primary calendar.

---
### `calendar.findFreeTime`
> Finds a free time slot for multiple people to meet....

```bash
mcpc @google tools-call calendar.findFreeTime attendees:="<val>" timeMin:="<val>" timeMax:="<val>" duration:="<val>"
```
**Arguments:**
- `attendees` **(Required)** `array`: The email addresses of the attendees.
- `timeMin` **(Required)** `string`: The start time for the search in strict ISO 8601 format with seconds and timezone (e.g., 2024-01-15T09:00:00Z or 2024-01-15T09:00:00-05:00).
- `timeMax` **(Required)** `string`: The end time for the search in strict ISO 8601 format with seconds and timezone (e.g., 2024-01-15T18:00:00Z or 2024-01-15T18:00:00-05:00).
- `duration` **(Required)** `number`: The duration of the meeting in minutes.

---
### `calendar.updateEvent`
> Updates an existing event in a calendar....

```bash
mcpc @google tools-call calendar.updateEvent eventId:="<val>"
```
**Arguments:**
- `eventId` **(Required)** `string`: The ID of the event to update.
- `calendarId` (Optional) `string`: The ID of the calendar to update the event in.
- `summary` (Optional) `string`: The new summary or title of the event.
- `description` (Optional) `string`: The new description of the event.
- `start` (Optional) `object`: 
- `end` (Optional) `object`: 
- `attendees` (Optional) `array`: The new list of attendees for the event.

---
### `calendar.respondToEvent`
> Responds to a meeting invitation (accept, decline, or tentative)....

```bash
mcpc @google tools-call calendar.respondToEvent eventId:="<val>" responseStatus:="<val>"
```
**Arguments:**
- `eventId` **(Required)** `string`: The ID of the event to respond to.
- `calendarId` (Optional) `string`: The ID of the calendar containing the event.
- `responseStatus` **(Required)** `string`: Your response to the invitation.
- `sendNotification` (Optional) `boolean`: Whether to send a notification to the organizer (default: true).
- `responseMessage` (Optional) `string`: Optional message to include with your response.

---
### `calendar.deleteEvent`
> Deletes an event from a calendar....

```bash
mcpc @google tools-call calendar.deleteEvent eventId:="<val>"
```
**Arguments:**
- `eventId` **(Required)** `string`: The ID of the event to delete.
- `calendarId` (Optional) `string`: The ID of the calendar to delete the event from. Defaults to the primary calendar.

---
### `chat.listSpaces`
> Lists the spaces the user is a member of....

```bash
mcpc @google tools-call chat.listSpaces 
```

---
### `chat.findSpaceByName`
> Finds a Google Chat space by its display name....

```bash
mcpc @google tools-call chat.findSpaceByName displayName:="<val>"
```
**Arguments:**
- `displayName` **(Required)** `string`: The display name of the space to find.

---
### `chat.sendMessage`
> Sends a message to a Google Chat space....

```bash
mcpc @google tools-call chat.sendMessage spaceName:="<val>" message:="<val>"
```
**Arguments:**
- `spaceName` **(Required)** `string`: The name of the space to send the message to (e.g., spaces/AAAAN2J52O8).
- `message` **(Required)** `string`: The message to send.
- `threadName` (Optional) `string`: The resource name of the thread to reply to. Example: "spaces/AAAAVJcnwPE/threads/IAf4cnLqYfg"

---
### `chat.getMessages`
> Gets messages from a Google Chat space....

```bash
mcpc @google tools-call chat.getMessages spaceName:="<val>"
```
**Arguments:**
- `spaceName` **(Required)** `string`: The name of the space to get messages from (e.g., spaces/AAAAN2J52O8).
- `threadName` (Optional) `string`: The resource name of the thread to filter messages by. Example: "spaces/AAAAVJcnwPE/threads/IAf4cnLqYfg"
- `unreadOnly` (Optional) `boolean`: Whether to return only unread messages.
- `pageSize` (Optional) `number`: The maximum number of messages to return.
- `pageToken` (Optional) `string`: The token for the next page of results.
- `orderBy` (Optional) `string`: The order to list messages in (e.g., "createTime desc").

---
### `chat.sendDm`
> Sends a direct message to a user....

```bash
mcpc @google tools-call chat.sendDm email:="<val>" message:="<val>"
```
**Arguments:**
- `email` **(Required)** `string`: The email address of the user to send the message to.
- `message` **(Required)** `string`: The message to send.
- `threadName` (Optional) `string`: The resource name of the thread to reply to. Example: "spaces/AAAAVJcnwPE/threads/IAf4cnLqYfg"

---
### `chat.findDmByEmail`
> Finds a Google Chat DM space by a user's email address....

```bash
mcpc @google tools-call chat.findDmByEmail email:="<val>"
```
**Arguments:**
- `email` **(Required)** `string`: The email address of the user to find the DM space with.

---
### `chat.listThreads`
> Lists threads from a Google Chat space in reverse chronological order....

```bash
mcpc @google tools-call chat.listThreads spaceName:="<val>"
```
**Arguments:**
- `spaceName` **(Required)** `string`: The name of the space to get threads from (e.g., spaces/AAAAN2J52O8).
- `pageSize` (Optional) `number`: The maximum number of threads to return.
- `pageToken` (Optional) `string`: The token for the next page of results.

---
### `chat.setUpSpace`
> Sets up a new Google Chat space with a display name and a list of members....

```bash
mcpc @google tools-call chat.setUpSpace displayName:="<val>" userNames:="<val>"
```
**Arguments:**
- `displayName` **(Required)** `string`: The display name of the space.
- `userNames` **(Required)** `array`: The user names of the members to add to the space (e.g. users/12345678)

---
### `gmail.search`
> Search for emails in Gmail using query parameters....

```bash
mcpc @google tools-call gmail.search 
```
**Arguments:**
- `query` (Optional) `string`: Search query (same syntax as Gmail search box, e.g., "from:someone@example.com is:unread").
- `maxResults` (Optional) `number`: Maximum number of results to return (default: 100).
- `pageToken` (Optional) `string`: Token for the next page of results.
- `labelIds` (Optional) `array`: Filter by label IDs (e.g., ["INBOX", "UNREAD"]).
- `includeSpamTrash` (Optional) `boolean`: Include messages from SPAM and TRASH (default: false).

---
### `gmail.get`
> Get the full content of a specific email message....

```bash
mcpc @google tools-call gmail.get messageId:="<val>"
```
**Arguments:**
- `messageId` **(Required)** `string`: The ID of the message to retrieve.
- `format` (Optional) `string`: Format of the message (default: full).

---
### `gmail.downloadAttachment`
> Downloads an attachment from a Gmail message to a local file....

```bash
mcpc @google tools-call gmail.downloadAttachment messageId:="<val>" attachmentId:="<val>" localPath:="<val>"
```
**Arguments:**
- `messageId` **(Required)** `string`: The ID of the message containing the attachment.
- `attachmentId` **(Required)** `string`: The ID of the attachment to download.
- `localPath` **(Required)** `string`: The absolute local path where the attachment should be saved (e.g., "/Users/name/downloads/report.pdf").

---
### `gmail.modify`
> Modify a Gmail message. Supported modifications include:     - Add labels to a message.     - Remove labels from a message. There are a list of system labels that can be modified on a message:     - I...

```bash
mcpc @google tools-call gmail.modify messageId:="<val>"
```
**Arguments:**
- `messageId` **(Required)** `string`: The ID of the message to add labels to and/or remove labels from.
- `addLabelIds` (Optional) `array`: A list of label IDs to add to the message. Limit to 100 labels.
- `removeLabelIds` (Optional) `array`: A list of label IDs to remove from the message. Limit to 100 labels.

---
### `gmail.send`
> Send an email message....

```bash
mcpc @google tools-call gmail.send to:="<val>" subject:="<val>" body:="<val>"
```
**Arguments:**
- `to` **(Required)** `any`: Recipient email address(es).
- `subject` **(Required)** `string`: Email subject.
- `body` **(Required)** `string`: Email body content.
- `cc` (Optional) `any`: CC recipient email address(es).
- `bcc` (Optional) `any`: BCC recipient email address(es).
- `isHtml` (Optional) `boolean`: Whether the body is HTML (default: false).

---
### `gmail.createDraft`
> Create a draft email message....

```bash
mcpc @google tools-call gmail.createDraft to:="<val>" subject:="<val>" body:="<val>"
```
**Arguments:**
- `to` **(Required)** `any`: Recipient email address(es).
- `subject` **(Required)** `string`: Email subject.
- `body` **(Required)** `string`: Email body content.
- `cc` (Optional) `any`: CC recipient email address(es).
- `bcc` (Optional) `any`: BCC recipient email address(es).
- `isHtml` (Optional) `boolean`: Whether the body is HTML (default: false).

---
### `gmail.sendDraft`
> Send a previously created draft email....

```bash
mcpc @google tools-call gmail.sendDraft draftId:="<val>"
```
**Arguments:**
- `draftId` **(Required)** `string`: The ID of the draft to send.

---
### `gmail.listLabels`
> List all Gmail labels in the user's mailbox....

```bash
mcpc @google tools-call gmail.listLabels 
```

---
### `time.getCurrentDate`
> Gets the current date. Returns both UTC (for calendar/API use) and local time (for display to the user), along with the timezone....

```bash
mcpc @google tools-call time.getCurrentDate 
```

---
### `time.getCurrentTime`
> Gets the current time. Returns both UTC (for calendar/API use) and local time (for display to the user), along with the timezone....

```bash
mcpc @google tools-call time.getCurrentTime 
```

---
### `time.getTimeZone`
> Gets the local timezone. Note: timezone is also included in getCurrentDate and getCurrentTime responses....

```bash
mcpc @google tools-call time.getTimeZone 
```

---
### `people.getUserProfile`
> Gets a user's profile information....

```bash
mcpc @google tools-call people.getUserProfile 
```
**Arguments:**
- `userId` (Optional) `string`: The ID of the user to get profile information for.
- `email` (Optional) `string`: The email address of the user to get profile information for.
- `name` (Optional) `string`: The name of the user to get profile information for.

---
### `people.getMe`
> Gets the profile information of the authenticated user....

```bash
mcpc @google tools-call people.getMe 
```

---
### `people.getUserRelations`
> Gets a user's relations (e.g., manager, spouse, assistant, etc.). Common relation types include: manager, assistant, spouse, partner, relative, mother, father, parent, sibling, child, friend, domestic...

```bash
mcpc @google tools-call people.getUserRelations 
```
**Arguments:**
- `userId` (Optional) `string`: The ID of the user to get relations for (e.g., "110001608645105799644" or "people/110001608645105799644"). Defaults to the authenticated user if not provided.
- `relationType` (Optional) `string`: The type of relation to filter by (e.g., "manager", "spouse", "assistant"). If not provided, returns all relations.

---
### `tasks.listLists`
> Lists the authenticated user's task lists....

```bash
mcpc @google tools-call tasks.listLists 
```
**Arguments:**
- `maxResults` (Optional) `number`: Maximum number of task lists to return.
- `pageToken` (Optional) `string`: Token for the next page of results.

---
### `tasks.list`
> Lists tasks in a specific task list....

```bash
mcpc @google tools-call tasks.list taskListId:="<val>"
```
**Arguments:**
- `taskListId` **(Required)** `string`: The ID of the task list.
- `showCompleted` (Optional) `boolean`: Whether to show completed tasks.
- `showDeleted` (Optional) `boolean`: Whether to show deleted tasks.
- `showHidden` (Optional) `boolean`: Whether to show hidden tasks.
- `showAssigned` (Optional) `boolean`: Whether to show tasks assigned from Docs or Chat.
- `maxResults` (Optional) `number`: Maximum number of tasks to return.
- `pageToken` (Optional) `string`: Token for the next page of results.
- `dueMin` (Optional) `string`: Lower bound for a task's due date (as a RFC 3339 timestamp).
- `dueMax` (Optional) `string`: Upper bound for a task's due date (as a RFC 3339 timestamp).

---
### `tasks.create`
> Creates a new task in the specified task list....

```bash
mcpc @google tools-call tasks.create taskListId:="<val>" title:="<val>"
```
**Arguments:**
- `taskListId` **(Required)** `string`: The ID of the task list.
- `title` **(Required)** `string`: The title of the task.
- `notes` (Optional) `string`: Notes for the task.
- `due` (Optional) `string`: The due date for the task (as a RFC 3339 timestamp).

---
### `tasks.update`
> Updates an existing task....

```bash
mcpc @google tools-call tasks.update taskListId:="<val>" taskId:="<val>"
```
**Arguments:**
- `taskListId` **(Required)** `string`: The ID of the task list.
- `taskId` **(Required)** `string`: The ID of the task to update.
- `title` (Optional) `string`: The new title of the task.
- `notes` (Optional) `string`: The new notes for the task.
- `status` (Optional) `string`: The new status of the task.
- `due` (Optional) `string`: The new due date for the task (as a RFC 3339 timestamp).

---
### `tasks.complete`
> Completes a task (convenience wrapper around update)....

```bash
mcpc @google tools-call tasks.complete taskListId:="<val>" taskId:="<val>"
```
**Arguments:**
- `taskListId` **(Required)** `string`: The ID of the task list.
- `taskId` **(Required)** `string`: The ID of the task to complete.

---
### `tasks.delete`
> Deletes a task....

```bash
mcpc @google tools-call tasks.delete taskListId:="<val>" taskId:="<val>"
```
**Arguments:**
- `taskListId` **(Required)** `string`: The ID of the task list.
- `taskId` **(Required)** `string`: The ID of the task to delete.

---
## @jira

### `atlassianUserInfo`
> Get current user info...

```bash
mcpc @jira tools-call atlassianUserInfo 
```

---
### `getAccessibleAtlassianResources`
> Get cloudid to make tool calls...

```bash
mcpc @jira tools-call getAccessibleAtlassianResources 
```

---
### `getJiraIssue`
> Get a Jira issue by issue id or key....

```bash
mcpc @jira tools-call getJiraIssue cloudId:="<val>" issueIdOrKey:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Unique identifier for an Atlassian Cloud instance in the form of a UUID. Can also be a site URL or extracted from Atlassian URLs - for example, from https://yoursite.atlassian.net/wiki/.... If not working, use the 'getAccessibleAtlassianResources' tool to find accessible Cloud IDs.
- `issueIdOrKey` **(Required)** `string`: Issue id or key can be used to uniquely identify an existing issue. Issue id is a numerical identifier. An example issue id is 10000. Issue key is formatted as a project key followed by a hyphen '-' character and then followed by a sequential number. An example issue key is ISSUE-1.
- `fields` (Optional) `array`: 
- `fieldsByKeys` (Optional) `boolean`: 
- `expand` (Optional) `string`: 
- `properties` (Optional) `array`: 
- `updateHistory` (Optional) `boolean`: 
- `failFast` (Optional) `boolean`: 

---
### `editJiraIssue`
> Update issue...

```bash
mcpc @jira tools-call editJiraIssue cloudId:="<val>" issueIdOrKey:="<val>" fields:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Cloud ID (UUID or site URL)
- `issueIdOrKey` **(Required)** `string`: Issue ID or key (e.g., PROJ-123 or 10000)
- `fields` **(Required)** `object`: 

---
### `createJiraIssue`
> Create issue...

```bash
mcpc @jira tools-call createJiraIssue cloudId:="<val>" projectKey:="<val>" issueTypeName:="<val>" summary:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Cloud ID (UUID or site URL)
- `projectKey` **(Required)** `string`: Project key
- `issueTypeName` **(Required)** `string`: Type (Task, Bug, Story)
- `summary` **(Required)** `string`: 
- `description` (Optional) `string`: Description (Markdown)
- `parent` (Optional) `string`: Parent for subtasks
- `assignee_account_id` (Optional) `string`: Assignee ID
- `additional_fields` (Optional) `object`: 

---
### `getTransitionsForJiraIssue`
> Get available transitions for an existing Jira issue id or key....

```bash
mcpc @jira tools-call getTransitionsForJiraIssue cloudId:="<val>" issueIdOrKey:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Unique identifier for an Atlassian Cloud instance in the form of a UUID. Can also be a site URL or extracted from Atlassian URLs - for example, from https://yoursite.atlassian.net/wiki/.... If not working, use the 'getAccessibleAtlassianResources' tool to find accessible Cloud IDs.
- `issueIdOrKey` **(Required)** `string`: Issue id or key can be used to uniquely identify an existing issue. Issue id is a numerical identifier. An example issue id is 10000. Issue key is formatted as a project key followed by a hyphen '-' character and then followed by a sequential number. An example issue key is ISSUE-1.
- `expand` (Optional) `string`: 
- `transitionId` (Optional) `string`: 
- `skipRemoteOnlyCondition` (Optional) `boolean`: 
- `includeUnavailableTransitions` (Optional) `boolean`: 
- `sortByOpsBarAndStatus` (Optional) `boolean`: 

---
### `getJiraIssueRemoteIssueLinks`
> Get remote issue links (eg: Confluence links etc...) of an existing Jira issue id or key...

```bash
mcpc @jira tools-call getJiraIssueRemoteIssueLinks cloudId:="<val>" issueIdOrKey:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Unique identifier for an Atlassian Cloud instance in the form of a UUID. Can also be a site URL or extracted from Atlassian URLs - for example, from https://yoursite.atlassian.net/wiki/.... If not working, use the 'getAccessibleAtlassianResources' tool to find accessible Cloud IDs.
- `issueIdOrKey` **(Required)** `string`: Issue id or key can be used to uniquely identify an existing issue. Issue id is a numerical identifier. An example issue id is 10000. Issue key is formatted as a project key followed by a hyphen '-' character and then followed by a sequential number. An example issue key is ISSUE-1.
- `globalId` (Optional) `string`: An identifier for the remote item in the remote system.             For example, the global ID for a remote item in Confluence would consist of the app ID and page ID, like this: appId=456&pageId=123.             When a global ID is provided, this tool returns only the remote issue link of the given Jira issue that has the provided global ID.             When no global ID is provided, this tool returns all the remote issue links of the given Jira issue.

---
### `getVisibleJiraProjects`
> Get projects...

```bash
mcpc @jira tools-call getVisibleJiraProjects cloudId:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Cloud ID (UUID or site URL)
- `searchString` (Optional) `string`: 
- `action` (Optional) `string`: 
- `startAt` (Optional) `number`: 
- `maxResults` (Optional) `number`: 
- `expandIssueTypes` (Optional) `boolean`: 

---
### `getJiraProjectIssueTypesMetadata`
> Get issue types...

```bash
mcpc @jira tools-call getJiraProjectIssueTypesMetadata cloudId:="<val>" projectIdOrKey:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Cloud ID (UUID or site URL)
- `projectIdOrKey` **(Required)** `string`: 
- `startAt` (Optional) `number`: 
- `maxResults` (Optional) `number`: 

---
### `getJiraIssueTypeMetaWithFields`
> Get issue type metadata for a project and issue type. Returns a page of field metadata for a specified project and issue type ID. Use the information to populate the requests in Create issue and Creat...

```bash
mcpc @jira tools-call getJiraIssueTypeMetaWithFields cloudId:="<val>" projectIdOrKey:="<val>" issueTypeId:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Unique identifier for an Atlassian Cloud instance in the form of a UUID. Can also be a site URL or extracted from Atlassian URLs - for example, from https://yoursite.atlassian.net/wiki/.... If not working, use the 'getAccessibleAtlassianResources' tool to find accessible Cloud IDs.
- `projectIdOrKey` **(Required)** `string`: The ID or key of the project
- `issueTypeId` **(Required)** `string`: The ID of the issue type
- `startAt` (Optional) `number`: The index of the first item to return (0-based)
- `maxResults` (Optional) `number`: The maximum number of items to return per page

---
### `addCommentToJiraIssue`
> Adds a comment to an existing Jira issue id or key....

```bash
mcpc @jira tools-call addCommentToJiraIssue cloudId:="<val>" issueIdOrKey:="<val>" commentBody:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Unique identifier for an Atlassian Cloud instance in the form of a UUID. Can also be a site URL or extracted from Atlassian URLs - for example, from https://yoursite.atlassian.net/wiki/.... If not working, use the 'getAccessibleAtlassianResources' tool to find accessible Cloud IDs.
- `issueIdOrKey` **(Required)** `string`: Issue id or key can be used to uniquely identify an existing issue. Issue id is a numerical identifier. An example issue id is 10000. Issue key is formatted as a project key followed by a hyphen '-' character and then followed by a sequential number. An example issue key is ISSUE-1.
- `commentBody` **(Required)** `string`: The content of the comment in Markdown format.
- `commentVisibility` (Optional) `object`: 

---
### `transitionJiraIssue`
> Transition an existing Jira issue (that has issue id or key) to a new status....

```bash
mcpc @jira tools-call transitionJiraIssue cloudId:="<val>" issueIdOrKey:="<val>" transition:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Unique identifier for an Atlassian Cloud instance in the form of a UUID. Can also be a site URL or extracted from Atlassian URLs - for example, from https://yoursite.atlassian.net/wiki/.... If not working, use the 'getAccessibleAtlassianResources' tool to find accessible Cloud IDs.
- `issueIdOrKey` **(Required)** `string`: Issue id or key can be used to uniquely identify an existing issue. Issue id is a numerical identifier. An example issue id is 10000. Issue key is formatted as a project key followed by a hyphen '-' character and then followed by a sequential number. An example issue key is ISSUE-1.
- `transition` **(Required)** `object`: 
- `fields` (Optional) `object`: 
- `update` (Optional) `object`: 
- `historyMetadata` (Optional) `object`: 

---
### `searchJiraIssuesUsingJql`
> Search Jira issues using Jira Query Language (JQL). ONLY use this tool when JQL syntax is specifically needed or mentioned in the query. For general searches across Jira and Confluence, use the unifie...

```bash
mcpc @jira tools-call searchJiraIssuesUsingJql cloudId:="<val>" jql:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Unique identifier for an Atlassian Cloud instance in the form of a UUID. Can also be a site URL or extracted from Atlassian URLs - for example, from https://yoursite.atlassian.net/wiki/.... If not working, use the 'getAccessibleAtlassianResources' tool to find accessible Cloud IDs.
- `jql` **(Required)** `string`: A Jira Query Language (JQL) expression to search Jira issues
- `maxResults` (Optional) `number`: A maximum number of issue to search per page. Default is 50, max is 100
- `fields` (Optional) `array`: 
- `nextPageToken` (Optional) `string`: This is used for pagination purpose to fetch more data if a JQL search has more issues in next pages

---
### `lookupJiraAccountId`
> Lookup user IDs...

```bash
mcpc @jira tools-call lookupJiraAccountId cloudId:="<val>" searchString:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Cloud ID (UUID or site URL)
- `searchString` **(Required)** `string`: 

---
### `addWorklogToJiraIssue`
> Add worklog...

```bash
mcpc @jira tools-call addWorklogToJiraIssue cloudId:="<val>" issueIdOrKey:="<val>" timeSpent:="<val>"
```
**Arguments:**
- `cloudId` **(Required)** `string`: Cloud ID (UUID or site URL)
- `issueIdOrKey` **(Required)** `string`: Issue ID or key (e.g., PROJ-123 or 10000)
- `timeSpent` **(Required)** `string`: Time (2h, 30m, 4d)
- `visibility` (Optional) `object`: 

---
### `search`
> Search Jira and Confluence using Rovo Search, ALWAYS use this tool to search for Jira and Confluence content unless the word CQL or JQL is used in the context...

```bash
mcpc @jira tools-call search query:="<val>"
```
**Arguments:**
- `query` **(Required)** `string`: The search query to use for Rovo Search

---
### `fetch`
> Get details of a Jira issue or Confluence page by ARI (Atlassian Resource Identifier), if the id is not an ARI, then use a different tool to fetch the content...

```bash
mcpc @jira tools-call fetch id:="<val>"
```
**Arguments:**
- `id` **(Required)** `string`: Atlassian Resource Identifier (ARI) from search results, e.g., "ari:cloud:jira:cloudId:issue/10107" or "ari:cloud:confluence:cloudId:page/123456789"

---
## @notion

### `notion-search`
> Perform a search over: - "internal": Semantic search over Notion workspace and connected sources (Slack, Google Drive, Github, Jira, Microsoft Teams, Sharepoint, OneDrive, Linear). Supports filtering ...

```bash
mcpc @notion tools-call notion-search query:="<val>"
```
**Arguments:**
- `query` **(Required)** `string`: Semantic search query over your entire Notion workspace and connected sources (Slack, Google Drive, Github, Jira, Microsoft Teams, Sharepoint, OneDrive, or Linear). For best results, don't provide more than one question per tool call. Use a separate "search" tool call for each search you want to perform. Alternatively, the query can be a substring or keyword to find users by matching against their name or email address. For example: "john" or "john@example.com"
- `query_type` (Optional) `string`: 
- `content_search_mode` (Optional) `string`: 
- `data_source_url` (Optional) `string`: Optionally, provide the URL of a Data source to search. This will perform a semantic search over the pages in the Data Source. Note: must be a Data Source, not a Database. <data-source> tags are part of the Notion flavored Markdown format returned by tools like fetch. The full spec is available in the create-pages tool description.
- `page_url` (Optional) `string`: Optionally, provide the URL or ID of a page to search within. This will perform a semantic search over the content within and under the specified page. Accepts either a full page URL (e.g. https://notion.so/workspace/Page-Title-1234567890) or just the page ID (UUIDv4) with or without dashes.
- `teamspace_id` (Optional) `string`: Optionally, provide the ID of a teamspace to restrict search results to. This will perform a search over content within the specified teamspace only. Accepts the teamspace ID (UUIDv4) with or without dashes.
- `filters` (Optional) `object`: Optionally provide filters to apply to the search results. Only valid when query_type is 'internal'.

---
### `notion-fetch`
> Retrieves details about a Notion entity (page or database) by URL or ID. Provide URL or ID in `id` parameter. Make multiple calls to fetch multiple entities. Pages use enhanced Markdown format. For th...

```bash
mcpc @notion tools-call notion-fetch id:="<val>"
```
**Arguments:**
- `id` **(Required)** `string`: The ID or URL of the Notion page to fetch

---
### `notion-create-pages`
> ## Overview Creates one or more Notion pages, with the specified properties and content. ## Parent All pages created with a single call to this tool will have the same parent. The parent can be a Noti...

```bash
mcpc @notion tools-call notion-create-pages pages:="<val>"
```
**Arguments:**
- `pages` **(Required)** `array`: The pages to create.
- `parent` (Optional) `any`: The parent under which the new pages will be created. This can be a page (page_id), a database page (database_id), or a data source/collection under a database (data_source_id). If omitted, the new pages will be created as private pages at the workspace level. Use data_source_id when you have a collection:// URL from the fetch tool.

---
### `notion-update-page`
> ## Overview Update a Notion page's properties or content. ## Properties Notion page properties are a JSON map of property names to SQLite values. For pages in a database: - ALWAYS use the "fetch" tool...

```bash
mcpc @notion tools-call notion-update-page data:="<val>"
```
**Arguments:**
- `data` **(Required)** `any`: The data required for updating a page

---
### `notion-move-pages`
> Move one or more Notion pages or databases to a new parent....

```bash
mcpc @notion tools-call notion-move-pages page_or_database_ids:="<val>" new_parent:="<val>"
```
**Arguments:**
- `page_or_database_ids` **(Required)** `array`: An array of up to 100 page or database IDs to move. IDs are v4 UUIDs and can be supplied with or without dashes (e.g. extracted from a <page> or <database> URL given by the "search" or "fetch" tool). Data Sources under Databases can't be moved individually.
- `new_parent` **(Required)** `any`: The new parent under which the pages will be moved. This can be a page, the workspace, a database, or a specific data source under a database when there are multiple. Moving pages to the workspace level adds them as private pages and should rarely be used.

---
### `notion-duplicate-page`
> Duplicate a Notion page. The page must be within the current workspace, and you must have permission to access it. The duplication completes asynchronously, so do not rely on the new page identified b...

```bash
mcpc @notion tools-call notion-duplicate-page page_id:="<val>"
```
**Arguments:**
- `page_id` **(Required)** `string`: The ID of the page to duplicate. This is a v4 UUID, with or without dashes, and can be parsed from a Notion page URL.

---
### `notion-create-database`
> Creates a new Notion database with the specified properties schema. If no title property provided, "Name" is auto-added. Returns Markdown with schema, SQLite definition, and data source ID in <data-so...

```bash
mcpc @notion tools-call notion-create-database properties:="<val>"
```
**Arguments:**
- `properties` **(Required)** `object`: The property schema of the new database. If no title property is provided, one will be automatically added.
- `parent` (Optional) `object`: The parent under which to create the new database. If omitted, the database will be created as a private page at the workspace level.
- `title` (Optional) `array`: The title of the new database, as a rich text object.
- `description` (Optional) `array`: The description of the new database, as a rich text object.

---
### `notion-update-data-source`
> Update a Notion data source's properties, name, or other attributes. Returns Markdown showing updated structure and schema. Accepts a data source ID (collection ID from fetch response's <data-source> ...

```bash
mcpc @notion tools-call notion-update-data-source data_source_id:="<val>"
```
**Arguments:**
- `data_source_id` **(Required)** `string`: The ID of the data source to update. Can be a data source ID (collection ID, from fetch response's <data-source> tag) or a database ID (only if the database has a single data source). UUID format with or without dashes.
- `title` (Optional) `array`: The new title of the data source as rich text.
- `description` (Optional) `array`: The new description of the data source as rich text.
- `properties` (Optional) `object`: Updates to the data source schema. Use null to remove a property, or provide `name` only to rename.
- `is_inline` (Optional) `boolean`: 
- `in_trash` (Optional) `boolean`: 

---
### `notion-create-comment`
> Add a comment to a page...

```bash
mcpc @notion tools-call notion-create-comment parent:="<val>" rich_text:="<val>"
```
**Arguments:**
- `parent` **(Required)** `object`: The parent of the comment. This must be a page.
- `rich_text` **(Required)** `array`: An array of rich text objects that represent the content of the comment.

---
### `notion-get-comments`
> Get all comments of a page...

```bash
mcpc @notion tools-call notion-get-comments page_id:="<val>"
```
**Arguments:**
- `page_id` **(Required)** `string`: Identifier for a Notion page.

---
### `notion-get-teams`
> Retrieves a list of teams (teamspaces) in the current workspace. Shows which teams exist, user membership status, IDs, names, and roles. Teams are returned split by membership status and limited to a ...

```bash
mcpc @notion tools-call notion-get-teams 
```
**Arguments:**
- `query` (Optional) `string`: Optional search query to filter teams by name (case-insensitive).

---
### `notion-get-users`
> Retrieves a list of users in the current workspace. Shows workspace members and guests with their IDs, names, emails (if available), and types (person or bot). Supports cursor-based pagination to iter...

```bash
mcpc @notion tools-call notion-get-users 
```
**Arguments:**
- `query` (Optional) `string`: Optional search query to filter users by name or email (case-insensitive).
- `start_cursor` (Optional) `string`: Cursor for pagination. Use the next_cursor value from the previous response to get the next page.
- `page_size` (Optional) `integer`: Number of users to return per page (default: 100, max: 100).
- `user_id` (Optional) `string`: Return only the user matching this ID. Pass "self" to fetch the current user.

---
