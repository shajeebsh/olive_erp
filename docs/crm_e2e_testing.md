# CRM E2E Testing Guide

## Overview
End-to-end testing scenarios for the Olive ERP CRM module.

---

## 1. Lead Creation

### Test Scenario: Create New Lead
1. Navigate to `/crm/leads/create/`
2. Fill form:
   - Lead Name: `Test Company Ltd`
   - Company: `Test Corp`
   - Email: `john@test.com`
   - Phone: `+1234567890`
   - Estimated Value: `50000`
   - Source: `Website`
3. Click "Save"
4. **Expected**: Redirect to lead list, new lead visible

### Test Scenario: Lead Pipeline Flow
```
NEW → CONTACTED → QUALIFIED → PROPOSAL → WON
```
1. Create lead (starts at NEW)
2. Move through stages via Kanban drag-drop
3. Verify stage change persists in database

---

## 2. Activity Logging

### Test Scenario: Log Call Activity
1. Navigate to lead detail page
2. Click "Add Activity"
3. Select Type: `Call`
4. Enter Subject: `Initial discovery call`
5. Mark Status: `Completed`
6. **Expected**: Activity appears in timeline

### Test Scenario: Activity Timeline
1. Open lead detail with multiple activities
2. Verify newest activity shows first
3. Check timestamp is accurate

---

## 3. Quote Generation

### Test Scenario: Create Quote from Lead
1. Navigate to lead detail
2. Click "Create Quote"
3. Add line items:
   - Product: `Consulting` | Qty: `10` | Price: `1000`
   - Product: `Setup` | Qty: `1` | Price: `500`
4. Set validity date
5. Click "Save as Draft"
6. **Expected**: Quote created with calculated totals

### Test Scenario: Send Quote to Customer
1. Open quote in Draft status
2. Click "Send to Customer"
3. **Expected**: Status changes to `SENT`, sent_at timestamp set

---

## 4. Quote to Invoice Conversion

### Test Scenario: Convert Accepted Quote
1. Create and send quote (see above)
2. Simulate customer acceptance
3. In admin/quote detail, click "Convert to Invoice"
4. **Expected**:
   - New Invoice created in Finance module
   - Quote status changed to `ACCEPTED`
   - Invoice linked to quote

---

## 5. Kanban Stage Transitions

### Test Scenario: Drag-and-Drop
1. Navigate to `/crm/leads/kanban/`
2. Drag lead card from NEW column
3. Drop onto CONTACTED column
4. **Expected**:
   - Lead moves to CONTACTED stage
   - HTMX request updates database
   - UI reflects new stage

### Test Scenario: Multiple Stage Transitions
1. Move lead through full pipeline:
   - NEW → CONTACTED → QUALIFIED → PROPOSAL → WON
2. Verify each transition is logged
3. Check conversion rate updates in summary

---

## 6. Lead Scoring

### Test Scenario: Score Calculation
1. Create lead with incomplete profile (score ~10)
2. Add 3 activities (score ~30)
3. Add company name and value (score +40)
4. **Expected**: Total score 80/100

---

## Test Data

```python
# Useful test queries
Lead.objects.filter(status='NEW')
Lead.objects.filter(status='WON').count()
Activity.objects.filter(lead=lead).count()
Quote.objects.filter(status='ACCEPTED')
```

---

## Known Issues & Fixes

| Issue | Fix |
|-------|-----|
| `NameError: models` not found | Import `Count` from `django.db.models` |
| Kanban not loading | Check Sortable.js CDN |
| Quote conversion failing | Ensure quote status is `ACCEPTED` |