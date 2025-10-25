# GitHub Issues Integration - Implementation Plan

## 1. Project Overview

### Goals
- View GitHub issues from enterprise repositories within the Tuido TUI app
- Reduce context switching between terminal and web browser
- Enable quick issue tracking for 5-10 active repositories
- Maintain visual consistency with existing Tuido design

### Scope - Version 1.0 (Read-Only)

**IN SCOPE:**
- View issues from selected repository (one at a time)
- Add/remove tracked repositories via UI
- Display essential fields: title, number, state, repo name
- Display important fields: labels, assignee, milestone, created/updated dates
- Filter by: creation/update date, labels, search text in title
- Live fetch (no caching)
- Enterprise GitHub Cloud authentication with PAT

**OUT OF SCOPE (Future):**
- Write operations (create, edit, close, comment on issues)
- Pull request details (we'll filter out PRs)
- Issue body preview or full details
- Comments viewing
- Linking to local tasks
- Notifications or webhooks

### User Requirements Summary
- Enterprise GitHub: `https://github.com/comcast-nse-ddos` (org)
- Base API URL: `https://api.github.com` (standard GitHub Enterprise Cloud)
- Authentication: Personal Access Token with SSO authorization
- 5-10 repositories to track
- Read-only access for v1

---

## 2. Technical Research Summary

### GitHub API Endpoints

**Primary Endpoint:**
```
GET /repos/{owner}/{repo}/issues
```

**Query Parameters We'll Use:**
- `state`: open, closed, all (default: open)
- `labels`: comma-separated label names
- `sort`: created, updated, comments (we'll use created/updated)
- `direction`: asc, desc
- `per_page`: max 100 (default: 30)
- `page`: pagination support
- `since`: ISO 8601 timestamp for filtering by update date

**Response Filtering:**
- Filter out PRs by checking for `pull_request` key in response
- Handle pagination via `Link` header

### Authentication

**Token Type:** Fine-grained Personal Access Token (recommended) or Classic PAT
**Required Permissions:** `issues:read` (for fine-grained tokens)
**SSO Consideration:** Token must be authorized for SSO after creation
**Header Format:** `Authorization: Bearer YOUR-TOKEN`

### Rate Limits
- Authenticated requests: 5,000 requests/hour
- Secondary limit: 100 concurrent requests max
- Check headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- For 10 repos refreshed periodically, we're well within limits

### Python Library
**Use PyGithub** for cleaner API interaction:
```python
from github import Github, Auth
auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
g = Github(auth=auth, base_url="https://api.github.com")
```

---

## 3. Architecture Design

### 3.1 New Data Models (`todo_tui/models.py`)

```python
@dataclass
class GitHubRepo:
    """A tracked GitHub repository."""
    id: str = field(default_factory=lambda: str(uuid4()))
    owner: str = ""  # e.g., "comcast-nse-ddos"
    name: str = ""   # e.g., "project-repo"
    display_name: str = ""  # Optional friendly name

@dataclass
class GitHubIssue:
    """A GitHub issue (cached from API response)."""
    number: int
    title: str
    state: str  # "open" or "closed"
    repo_full_name: str  # "owner/repo"
    labels: List[str]  # Label names
    assignee: Optional[str]  # Username or None
    milestone: Optional[str]  # Milestone title or None
    created_at: str  # ISO timestamp
    updated_at: str  # ISO timestamp
    html_url: str  # Link to issue on GitHub

@dataclass
class GitHubSettings:
    """GitHub integration settings (embedded in Settings model)."""
    enabled: bool = False
    personal_access_token: str = ""  # Store encrypted or in env
    tracked_repos: List[GitHubRepo] = field(default_factory=list)
```

**Update existing `Settings` model** to include `github: GitHubSettings`

### 3.2 API Client Module (`todo_tui/github_client.py`)

```python
class GitHubClient:
    """Client for GitHub API operations."""

    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        self.auth = Auth.Token(token)
        self.client = Github(auth=self.auth, base_url=base_url)

    def test_connection(self) -> bool:
        """Test API connection and token validity."""

    def get_rate_limit(self) -> dict:
        """Get current rate limit status."""

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: Optional[List[str]] = None,
        sort: str = "created",
        direction: str = "desc",
        since: Optional[str] = None,
    ) -> List[GitHubIssue]:
        """Fetch issues for a repository (filters out PRs)."""

    def search_issues(
        self,
        owner: str,
        repo: str,
        query: str,
        state: str = "open"
    ) -> List[GitHubIssue]:
        """Search issues by text in title."""
```

### 3.3 UI Component Structure

**New Tab in Main Content Area** (similar to Scratchpad/Snippets tabs):

```
GitHubIssuesPanel (Container)
├── Left Column (30% width)
│   ├── Repository Selector (ListView)
│   │   └── [+ Add Repo] button at bottom
│   └── Filter Controls (Container)
│       ├── State dropdown (Open/Closed/All)
│       ├── Sort dropdown (Created/Updated)
│       ├── Label filter (input)
│       └── [Refresh] button
└── Right Column (70% width)
    ├── Issue List (ListView or DataTable)
    │   └── Issue rows with: #number, title, labels, assignee, dates
    └── Issue Detail View (Optional for v1, or just show in list)
```

**New Widget Files:**
- `todo_tui/widgets/github_issues.py` - Main panel
- `todo_tui/widgets/dialogs.py` - Add `AddRepoDialog` class

### 3.4 Settings Integration

**Add to Settings Dialog:**
- GitHub section with:
  - Enable/Disable toggle
  - PAT input field (masked)
  - Test Connection button
  - Tracked repositories list with add/remove

### 3.5 Storage Considerations

**Settings Storage:**
- GitHub settings stored in `settings.json` (existing pattern)
- **Security consideration:** PAT stored in plaintext in settings file
  - Alternative: Use environment variable and only store flag
  - v1: Accept plaintext risk (local file permissions), document best practice

**No Issue Caching:**
- Issues fetched live on demand
- No persistent storage needed

---

## 4. UI/UX Design

### 4.1 Overall Layout

**New Tab:** `GitHub Issues` (add after Snippets tab)
- Icon: `Icons.GITHUB` (or `Icons.BOOK` as fallback)
- Layout: Horizontal split (similar to Tasks tab)

### 4.2 Repository Selector

**Left sidebar component:**
- List of tracked repos (owner/name format)
- Current selected repo highlighted
- `[+]` button at bottom to add new repo
- `[-]` button to remove selected repo (with confirmation)
- Empty state: "No repositories tracked. Click + to add one."

### 4.3 Issue List

**Main content area:**
- Table or ListView showing:
  - `#123` (number in muted color)
  - `Title` (bold, truncated if long)
  - `[label] [label]` (colored badges using Catppuccin palette)
  - `@assignee` (if assigned)
  - `📌 milestone-name` (if set)
  - `Created: Jan 25` | `Updated: Jan 26` (relative or absolute dates)
  - `🟢 Open` or `🔴 Closed` (state indicator)

**Interactions:**
- Click issue to open in browser (using `webbrowser.open(issue.html_url)`)
- Keyboard navigation (up/down arrows)
- Enter to open in browser

### 4.4 Filter Controls

**Below repository selector:**
- State filter: Radio buttons or dropdown (Open/Closed/All)
- Sort: Dropdown (Created ↓, Created ↑, Updated ↓, Updated ↑)
- Label filter: Text input (comma-separated labels)
- Search: Text input (search in title)
- Refresh button: Force re-fetch from API

### 4.5 Visual Design

**Follow existing Catppuccin theme:**
- Border colors: `$panel` with `$secondary` on focus
- Surface background: `$surface`
- Label colors: Map to Catppuccin palette (red, green, blue, yellow, etc.)
- State indicators: Green for open, red for closed
- Consistent padding and spacing with other tabs

---

## 5. Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)
1. **Add PyGithub dependency** to `pyproject.toml`
2. **Create data models** in `models.py`:
   - `GitHubRepo`, `GitHubIssue`, `GitHubSettings`
   - Update `Settings` model
3. **Create API client** (`github_client.py`):
   - Basic client initialization
   - `test_connection()` method
   - `list_issues()` method with PR filtering
4. **Update storage** to handle GitHub settings

### Phase 2: Settings UI (Week 1)
1. **Extend SettingsDialog** in `dialogs.py`:
   - Add GitHub settings section
   - PAT input field (masked)
   - Enable/disable toggle
   - Test connection button with feedback
2. **Test authentication** with your enterprise PAT

### Phase 3: Basic GitHub Tab UI (Week 2)
1. **Create `GitHubIssuesPanel`** in `widgets/github_issues.py`:
   - Basic layout: horizontal split
   - Left: Repository selector (ListView)
   - Right: Issue list placeholder
2. **Add tab** to main app (`app.py`)
3. **Implement repository selector**:
   - Load from settings
   - Display repos
   - Selection handling
4. **Create `AddRepoDialog`**:
   - Input for owner/repo
   - Validation
   - Save to settings

### Phase 4: Issue List Display (Week 2)
1. **Implement issue fetching**:
   - On repo selection, fetch issues
   - Show loading indicator
   - Display issues in ListView or DataTable
2. **Format issue rows**:
   - Number, title, labels, assignee, dates
   - State indicator
3. **Open in browser** on click/enter

### Phase 5: Filtering & Search (Week 3)
1. **Add filter controls** below repo selector:
   - State filter (open/closed/all)
   - Sort dropdown
   - Label filter input
   - Search text input
2. **Implement filter logic**:
   - Build query parameters from filters
   - Re-fetch on filter change
   - Show loading state
3. **Add refresh button**

### Phase 6: Polish & Error Handling (Week 3)
1. **Error handling**:
   - Network errors (show ErrorDialog)
   - Invalid PAT (show helpful message)
   - Rate limit exceeded (show remaining/reset time)
   - Empty states (no issues, no repos)
2. **Loading states**:
   - Show spinner during API calls
   - Disable controls while loading
3. **Keyboard bindings**:
   - Add bindings to footer (r for refresh, etc.)
4. **Documentation**:
   - Update README with GitHub setup instructions
   - Document PAT creation with SSO authorization

---

## 6. Security & Best Practices

### PAT Storage Options

**Option 1: Settings file (v1 approach)**
- Store in `settings.json` (plaintext)
- Pros: Simple, no external dependencies
- Cons: Token visible in plaintext on disk
- Mitigation: Document file permissions best practices

**Option 2: Environment variable**
- Store in `.env` file or system environment
- Pros: More secure, separated from app config
- Cons: Requires user setup, less convenient
- Implementation: Check env var first, fallback to settings

**Recommendation for v1:** Option 1 with clear documentation about security implications and Option 2 as future enhancement.

### SSO Authorization

**User instructions:**
1. Create fine-grained PAT at https://github.com/settings/tokens?type=beta
2. Grant `issues:read` permission for repositories
3. **After creation, authorize for SSO:** Click "Configure SSO" → Authorize for comcast-nse-ddos org
4. Copy token and paste into Tuido settings

### Rate Limit Handling

**Strategy:**
- Display rate limit status in UI (remaining/total)
- If near limit (< 100 remaining), show warning
- If exceeded, show error with reset time
- Cache rate limit info from response headers

### Error Handling

**Error scenarios:**
- Network error: "Cannot connect to GitHub. Check your internet connection."
- 401 Unauthorized: "Invalid token. Please check your PAT in settings."
- 403 Forbidden (SSO): "Token not authorized for SSO. Please authorize in GitHub settings."
- 404 Not Found: "Repository not found. Check owner/repo name."
- 422 Validation Failed: "Invalid request parameters."

---

## 7. Testing Strategy

### Manual Testing Checklist

**Authentication:**
- [ ] Test with valid PAT
- [ ] Test with invalid PAT
- [ ] Test with PAT not authorized for SSO
- [ ] Test connection from settings dialog

**Repository Management:**
- [ ] Add repository (valid)
- [ ] Add repository (invalid owner/name)
- [ ] Remove repository
- [ ] Select different repositories
- [ ] Empty state (no repos)

**Issue Listing:**
- [ ] Fetch issues from repo with issues
- [ ] Fetch from repo with no issues
- [ ] Verify PRs are filtered out
- [ ] Pagination (repo with >30 issues)
- [ ] Labels display correctly
- [ ] Assignee display
- [ ] Milestone display
- [ ] Date formatting

**Filtering:**
- [ ] Filter by state (open/closed/all)
- [ ] Filter by label
- [ ] Search by title text
- [ ] Sort by created/updated
- [ ] Combined filters

**Error Handling:**
- [ ] Network disconnect during fetch
- [ ] Rate limit exceeded
- [ ] Invalid filter parameters

**UI/UX:**
- [ ] Keyboard navigation
- [ ] Open issue in browser
- [ ] Loading states
- [ ] Theme consistency
- [ ] Responsive layout

### Mock Data for Development

Create test fixtures with sample issues to develop UI without API calls:
```python
# For development/testing
MOCK_ISSUES = [
    GitHubIssue(
        number=123,
        title="Fix authentication bug",
        state="open",
        labels=["bug", "priority-high"],
        assignee="johndoe",
        milestone="v2.0",
        created_at="2025-01-20T10:00:00Z",
        updated_at="2025-01-25T14:30:00Z",
        repo_full_name="comcast-nse-ddos/example-repo",
        html_url="https://github.com/comcast-nse-ddos/example-repo/issues/123"
    ),
    # ... more mock issues
]
```

---

## 8. Future Enhancements (Post-v1)

### Phase 2 Features (Write Operations)
- Create new issue
- Close/reopen issue
- Add comment to issue
- Edit issue title/description
- Add/remove labels
- Assign/unassign users

### Phase 3 Features (Advanced)
- View issue comments
- View issue events (timeline)
- Filter by assignee
- Filter by milestone
- Multi-repo view (aggregate issues from all tracked repos)
- Issue notifications (new issues, updates)

### Phase 4 Features (Integration)
- Link GitHub issue to local task
- Auto-create local task from GitHub issue
- Sync issue state with task completion
- Two-way sync

### UX Improvements
- Issue detail pane (split view: list + details)
- Rich text preview for issue body (Markdown rendering)
- Label color customization
- Relative date formatting ("2 days ago")
- Search across all repos
- Saved filter presets

---

## 9. Dependencies

### New Python Packages
Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies
    "PyGithub>=2.3.0",
]
```

### Existing Dependencies (No Changes)
- `textual` - TUI framework
- `python-dotenv` - Environment variables (can use for PAT)
- `pyperclip` - Clipboard (for copying issue URLs)

---

## 10. File Structure Summary

### New Files
```
todo_tui/
├── github_client.py          # GitHub API client
└── widgets/
    └── github_issues.py       # Main GitHub issues panel UI
```

### Modified Files
```
todo_tui/
├── models.py                  # Add GitHubRepo, GitHubIssue, GitHubSettings
├── app.py                     # Add GitHub tab
└── widgets/
    └── dialogs.py             # Add AddRepoDialog, extend SettingsDialog
```

---

## 11. Success Criteria

**v1.0 Complete When:**
- ✅ Can authenticate with enterprise GitHub PAT
- ✅ Can add/remove tracked repositories
- ✅ Can view issues from selected repository
- ✅ Can filter by state, labels, and search text
- ✅ Can sort by created/updated date
- ✅ Can open issues in browser
- ✅ Error handling for common scenarios
- ✅ UI matches existing Tuido design patterns
- ✅ Documentation for setup and usage

---

## 12. Timeline Estimate

**Total: 2-3 weeks** (assuming part-time development)

- Week 1: Core infrastructure, settings, API client
- Week 2: UI components, basic issue display
- Week 3: Filtering, polish, testing, documentation

---

## 13. Next Steps

1. **Review and approve this plan** ✅
2. **Create PAT** for testing (with SSO authorization)
3. **Start with Phase 1** (dependencies and data models)
4. **Iterate and test** throughout development
5. **Save progress** to avoid losing work in fresh sessions

---

## 14. Implementation Progress Tracking

### Phase 1: Core Infrastructure
- [ ] Add PyGithub dependency to `pyproject.toml`
- [ ] Create `GitHubRepo` data model
- [ ] Create `GitHubIssue` data model
- [ ] Create `GitHubSettings` data model
- [ ] Update `Settings` model with GitHub settings
- [ ] Create `github_client.py` with basic client structure
- [ ] Implement `test_connection()` method
- [ ] Implement `get_rate_limit()` method
- [ ] Implement `list_issues()` method
- [ ] Update storage to serialize/deserialize GitHub settings

### Phase 2: Settings UI
- [ ] Add GitHub section to `SettingsDialog`
- [ ] Add enable/disable toggle
- [ ] Add PAT input field (masked)
- [ ] Add test connection button
- [ ] Add repository list display
- [ ] Add add/remove repo buttons
- [ ] Test with real PAT

### Phase 3: Basic GitHub Tab UI
- [ ] Create `GitHubIssuesPanel` widget file
- [ ] Implement basic horizontal layout
- [ ] Add repository selector (ListView)
- [ ] Create `AddRepoDialog`
- [ ] Add tab to main app
- [ ] Wire up repository selection

### Phase 4: Issue List Display
- [ ] Implement issue fetching on repo selection
- [ ] Add loading indicator
- [ ] Create issue list view
- [ ] Format issue rows (number, title, state)
- [ ] Add labels display
- [ ] Add assignee display
- [ ] Add milestone display
- [ ] Add date formatting
- [ ] Implement "open in browser" functionality

### Phase 5: Filtering & Search
- [ ] Add state filter control
- [ ] Add sort control
- [ ] Add label filter input
- [ ] Add search text input
- [ ] Add refresh button
- [ ] Implement filter logic
- [ ] Show loading during filter changes

### Phase 6: Polish & Error Handling
- [ ] Add error dialogs for common scenarios
- [ ] Add rate limit display
- [ ] Add empty states
- [ ] Add keyboard bindings
- [ ] Test all error scenarios
- [ ] Update README with setup instructions
- [ ] Document PAT creation with SSO
