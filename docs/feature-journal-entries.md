# docs/feature-journal-entries.md — Journal Entries Screen Reference

## Overview

The Journal Entries screen at `/finance/journal/` provides a compact, ledger-style view of all double-entry accounting transactions for the active company.

**Template:** `templates/finance/journal.html`  
**View:** `finance.views.JournalEntryListView`  
**URL name:** `finance:journal`

---

## Layout Architecture

The screen uses a CSS-only compact ledger layout with no external JS dependencies.

### Entry Structure

Each journal entry renders as a self-contained card with three sections:

```
┌─────────────────────────────────────────────────────────────┐
│  JE-001  │  07 Apr 2026  │  POSTED  │              admin   │  ← .je-header
├──────────┬────────────────┬──────────┬──────────┤
│  Code    │  Account       │  Debit   │  Credit  │  ← .je-col-headers
├──────────┼────────────────┼──────────┼──────────┤
│  1100    │  Cash          │  1,000   │          │  ← .je-line
│  4000    │  Sales Revenue │          │  1,000   │  ← .je-line
├──────────┴────────────────┴──────────┴──────────┤
│  Optional memo text                                │  ← .je-memo
└─────────────────────────────────────────────────────────────┘
```

### CSS Grid Layout

The `.je-col-headers` and `.je-line` elements use an identical 4-column CSS Grid:

```css
grid-template-columns: 48px 1fr 64px 64px;
                        code  name debit credit
```

**Page container:** Uses `.report-page` with max-width 900px (not --wide) for a tighter, more account-wise side-by-side layout.

**Key change (April 2026):** The description column was removed from the main ledger lines. Line-level descriptions are now secondary metadata rendered in `.je-memo` (entry-level memo) rather than driving horizontal width. The layout is now compact and efficient, not stretched.

### CSS Classes

| Class              | Element         | Purpose                                   |
|--------------------|-----------------|-------------------------------------------|
| `.je-page`         | page wrapper    | Outer container (max-width: 900px)       |
| `.je-filter-bar`   | form wrapper    | Filter controls bar                      |
| `.je-entry`        | entry card      | Single journal entry card                |
| `.je-header`       | flex row        | Entry metadata (number, date, status, user)|
| `.je-number`       | span            | Bold entry reference number               |
| `.je-date`         | span            | Entry date                                |
| `.je-badge`        | span            | Status badge (`.posted` / `.draft`)       |
| `.je-user`         | span            | Created-by username (right-aligned)      |
| `.je-col-headers` | grid row        | Column header labels inside each entry    |
| `.je-lines`        | lines container | Wrapper for all line rows                |
| `.je-line`         | grid row        | Single debit/credit line (4 columns)     |
| `.je-code`         | grid cell 1     | Account code (monospace, 48px)           |
| `.je-name`         | grid cell 2     | Account name (1fr, truncated)            |
| `.je-debit`        | grid cell 3     | Debit amount (64px, right-aligned, red)  |
| `.je-credit`       | grid cell 4     | Credit amount (64px, right-aligned, green)|
| `.je-memo`         | footer div      | Entry-level memo/description              |
| `.je-empty`        | empty state     | Shown when no entries match filters       |

---

## Filter Bar

The filter bar renders a compact single-row form:

| Filter       | Input type    | Query param | Filter applied on               |
|--------------|---------------|-------------|----------------------------------|
| Account      | `<select>`    | `account`   | `JournalEntryLine.account.id`   |
| Status       | `<select>`    | `status`    | `posted` / `draft`              |
| Date From    | `date`        | `date_from` | `entry.date >= date_from`       |
| Date To      | `date`        | `date_to`   | `entry.date <= date_to`         |
| Search       | `text`        | `q`         | `entry_number` or description   |

Context variables passed to template:
- `entries` — queryset of `JournalEntry` with `lines.all()` prefetched
- `accounts` — all `Account` objects for the company (for the dropdown)
- `account_filter`, `status_filter`, `date_from`, `date_to`, `query` — current filter values

---

## Responsiveness

| Breakpoint  | Layout change                                     |
|-------------|--------------------------------------------------|
| `> 600px`   | Full 4-column grid (48px 1fr 64px 64px)         |
| `≤ 600px`   | Compact 4-column (42px 1fr 52px 52px)          |

---

## Styling Location

All journal entry CSS is in a `{% block extra_css %}` `<style>` block **local to the template** (`templates/finance/journal.html`). This avoids polluting the global stylesheet with screen-specific rules.

The `{% block extra_css %}` is rendered inside `<head>` by `base.html` — the block exists and is verified working.

---

## Empty State

When no entries match the current filters, the template renders:
```html
<div class="je-empty">
    <i class="bi bi-journal-text"></i>
    <p>No journal entries found.</p>
    <a href="{% url 'finance:journal_create' %}">Create First Entry</a>
</div>
```

---

## Known Constraints

- Line prefetch: `entry.lines.all` triggers N+1 queries for large entry sets. Add `prefetch_related('lines__account')` to the view queryset for production performance.
- Account names are truncated at 28 characters in the template. Adjust `truncatechars:28` in the template if more space is needed.