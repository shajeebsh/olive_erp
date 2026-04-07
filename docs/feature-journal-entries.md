# docs/feature-journal-entries.md — Journal Entries Screen Reference

## Overview

The Journal Entries screen at `/finance/journal/` provides a compact, card-grid view of all double-entry accounting transactions for the active company.

**Template:** `templates/finance/journal.html`  
**View:** `finance.views.JournalEntryListView`  
**URL name:** `finance:journal`

---

## Layout Architecture (April 2026 — Card Grid)

The screen uses a CSS-only compact card-grid layout with no external JS dependencies.

### Card Structure

Each journal entry renders as a self-contained card:

```
┌──────────────────────────────────────────────────────────┐
│ JE-001                    [POSTED]                      │  ← .je-card-header
│ 07 Apr 2026                                         │
├──────────────────────────────────────────────────────────┤
│ 📝 Payment from Acme Corp                             │  ← .je-card-summary (optional)
├────────────────────┬─────────────┬──────────┬───────────┤
│ Code  │ Account    │ Debit      │ Credit   │           │  ← .je-ledger-table
├───────┼────────────┼────────────┼──────────┤
│ 1100  │ Cash       │ 1,000.00   │          │
│ 4000  │ Sales Rev. │            │ 1,000.00 │
├────────────────────┴─────────────┴──────────┴───────────┤
│                              Total: €1,000.00          │  ← .je-card-footer
└──────────────────────────────────────────────────────────┘
```

### Grid Layout

The `.je-grid` container uses CSS Grid for responsive layout:

```css
.je-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);  /* 2 columns on desktop */
    gap: 0.75rem;
}
@media (max-width: 900px) {
    .je-grid { grid-template-columns: 1fr; }  /* 1 column on tablet/mobile */
}
```

### Key Features

- **2-column card grid** on desktop (where space allows)
- **Responsive collapse** to 1 column on smaller screens
- **Card header** with entry number, date, and status badge
- **Optional summary line** for memo/description (muted, truncated)
- **Mini ledger table** inside each card with aligned columns
- **Footer total row** showing total debit amount
- **Color coding**: 
  - Posted badge: green background (`#dcfce7`), green text (`#15803d`)
  - Draft badge: yellow background (`#fef3c7`), amber text (`#92400e`)
  - Debit amounts: red text (`#b91c1c`)
  - Credit amounts: green text (`#15803d`)

### CSS Classes

| Class              | Element         | Purpose                                   |
|--------------------|-----------------|-------------------------------------------|
| `.je-page`         | page wrapper    | Outer container (max-width 1200px)       |
| `.je-filter-bar`   | form wrapper    | Filter controls bar                      |
| `.je-grid`         | grid container  | 2-column card grid wrapper              |
| `.je-card`         | entry card      | Single journal entry card                |
| `.je-card-header`  | flex row        | Entry number, date, badge                |
| `.je-number`       | span            | Bold entry reference number              |
| `.je-date`         | span            | Entry date (muted)                      |
| `.je-badge`        | span            | Status badge (`.posted` / `.draft`)    |
| `.je-card-summary` | div             | Memo/description line (optional)        |
| `.je-ledger-table` | table           | Mini ledger inside card                 |
| `.je-account-code` | td             | Account code (monospace)               |
| `.je-account-name` | td             | Account name (truncated)               |
| `.je-debit`        | td              | Debit amount (red, right-aligned)       |
| `.je-credit`       | td              | Credit amount (green, right-aligned)   |
| `.je-card-footer`  | div             | Total row at bottom of card             |
| `.je-empty`        | empty state     | Shown when no entries match filters     |

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

## Model Properties

The `JournalEntry` model has computed properties for totals:

```python
@property
def total_debit(self):
    return sum(line.debit for line in self.lines.all())

@property
def total_credit(self):
    return sum(line.credit for line in self.lines.all())
```

---

## Responsiveness

| Breakpoint  | Layout change                                     |
|-------------|--------------------------------------------------|
| `> 900px`   | 2-column card grid                               |
| `≤ 900px`   | Single column card grid                         |
| `≤ 600px`   | Compact card padding, smaller fonts              |

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
- Account names are truncated at 25 characters in the ledger table. Adjust `truncatechars:25` in the template if more space is needed.
- The card footer total shows `total_debit`. In balanced entries, this equals `total_credit`.