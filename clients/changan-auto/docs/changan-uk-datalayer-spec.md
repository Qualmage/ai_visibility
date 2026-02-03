# Changan UK DataLayer Specification

## Lead Tracking for Form Submissions

**Version:** 1.0
**Date:** 2026-01-28
**Property:** changanuk.com

---

## Overview

This document specifies the dataLayer implementation required to track form submissions and lead sources on changanuk.com. The implementation enables:

1. **Form-to-API Value Mapping** - Pass `Cluesourcesecond` and `Cluesourcethird` values to ESS API
2. **Origin Tracking** - Capture and persist the traffic source across sessions

---

## Questions for Manny (Before Implementation)

Before proceeding with development, we need clarification on the following:

### Question 1: URL Parameter Format

**Can partners use standard UTM parameters instead of a custom `origin` parameter?**

| Option | URL Example | GA4 Tracking | Custom Code Needed |
|--------|-------------|--------------|-------------------|
| **A: UTM (Recommended)** | `?utm_source=haymarket` | Automatic | Only for ESS API |
| **B: Custom origin** | `?origin=haymarket` | Requires custom setup | For GA4 + ESS API |

**Why this matters:** UTM parameters are industry standard and GA4 captures them automatically. Using `?utm_source=haymarket&utm_medium=referral` instead of `?origin=haymarket` reduces implementation complexity.

**Recommendation:** Use UTM parameters if possible.

### Question 2: What Should `origin` Capture?

What values do you expect in the `origin` field? Please confirm:

- [ ] Partner name only (e.g., `haymarket`) - requires tagged URLs
- [ ] Referrer domain (e.g., `haymarket.com`) - automatic fallback
- [ ] Full referrer URL (e.g., `https://haymarket.com/article/changan`) - more detail
- [ ] All of the above with priority: URL param > referrer domain

### Question 3: ESS API Field Confirmation

Please confirm the exact ESS API field names and expected values:

| Field Name | Expected Values | Notes |
|------------|-----------------|-------|
| `Cluesourcesecond` | "Official Website-Online" | Same for all forms? |
| `Cluesourcethird` | Form name | Exact spelling required |
| `origin` | Traffic source | Is this the correct field name? |

### Question 4: Existing Form Implementation

How are forms currently submitted to the ESS API?

- [ ] Native HTML form POST
- [ ] JavaScript/AJAX fetch/XHR
- [ ] Third-party form handler (e.g., HubSpot, Pardot)
- [ ] CMS built-in (e.g., WordPress plugin)

**Why this matters:** Determines how LaunchVox will add the tracking fields.

---

## GA4 Default Behaviour (For Reference)

**Important:** GA4 already captures traffic source information automatically. This section clarifies what's built-in vs what requires custom implementation.

### What GA4 Captures Automatically (No Code Needed)

| Dimension | How It's Captured | Example Value |
|-----------|-------------------|---------------|
| `sessionSource` | Referrer header or UTM params | `google`, `haymarket.com`, `(direct)` |
| `sessionMedium` | Referrer header or UTM params | `organic`, `referral`, `cpc`, `(none)` |
| `sessionCampaign` | `utm_campaign` parameter | `spring_promo` |
| `firstUserSource` | First-ever traffic source | Persists forever for that user |
| `page_referrer` | HTTP referrer header | `https://google.com/search?q=...` |

### UTM Parameters GA4 Reads Automatically

```
https://www.changanuk.com/?utm_source=haymarket&utm_medium=referral&utm_campaign=ev_launch
```

| Parameter | GA4 Dimension | Example |
|-----------|---------------|---------|
| `utm_source` | sessionSource | `haymarket` |
| `utm_medium` | sessionMedium | `referral` |
| `utm_campaign` | sessionCampaign | `ev_launch` |
| `utm_term` | sessionManualTerm | `electric cars` |
| `utm_content` | sessionManualAdContent | `banner_ad` |

### What Requires Custom Implementation

| Requirement | GA4 Default? | Custom Needed? |
|-------------|--------------|----------------|
| Track traffic source in GA4 | **Yes** (via UTM or referrer) | No |
| Custom `?origin=` parameter | **No** | Yes - GTM must capture it |
| Pass data to ESS API | **No** | Yes - website code |
| `Cluesourcesecond` field | **No** | Yes - ESS API specific |
| `Cluesourcethird` field | **No** | Yes - ESS API specific |
| Persist source across session | **Yes** (GA4 does this) | Only for ESS API side |

### Recommendation

**For GA4 Analytics:** Use standard UTM parameters. Works automatically.

**For ESS API Integration:** Custom implementation required regardless of URL parameter format.

**Simplest Path:**
1. Partners use UTM parameters (GA4 just works)
2. GTM reads `utm_source` and stores in sessionStorage
3. LaunchVox passes to ESS API

This approach uses industry standards and minimises custom code.

---

## Responsibilities

| Team | Responsibility |
|------|----------------|
| **LaunchVox** (Website Development) | Implement dataLayer pushes, ESS API integration, read origin from sessionStorage |
| **Alchemy** (GTM & Analytics) | Configure GTM variables/triggers/tags, GA4 tracking, origin parameter capture |

---

## Part 1: Origin Capture (URL Parameter + Referrer Fallback)

### How It Works

1. User lands on site - GTM captures the traffic source automatically
2. **Priority 1:** Explicit URL parameter (e.g., `?origin=haymarket`)
3. **Priority 2:** Referrer header (e.g., user came from `haymarket.com`)
4. **Priority 3:** Empty string (direct traffic)
5. Value is stored in `sessionStorage` and persists across the session
6. **Website** (LaunchVox) reads from `sessionStorage` when submitting forms

### Traffic Source Examples

| Scenario | URL | Referrer | Captured Origin |
|----------|-----|----------|-----------------|
| Tagged partner link | `changanuk.com/?origin=haymarket` | haymarket.com | `haymarket` (from URL param) |
| Untagged partner link | `changanuk.com/` | haymarket.com | `haymarket.com` (from referrer) |
| Google organic | `changanuk.com/` | google.com | `google.com` (from referrer) |
| Direct traffic | `changanuk.com/` | (empty) | `` (empty string) |
| Internal navigation | `changanuk.com/test-drive` | changanuk.com | (no change - keeps original) |

### Alchemy Implements (GTM)

GTM will automatically capture the traffic source on landing and store it:

```javascript
// This runs via GTM on all pages (fires once per session on landing)
(function() {
  // Skip if we already have an origin stored (not first pageview)
  if (sessionStorage.getItem('changan_origin_set')) {
    return;
  }

  var origin = '';

  // Priority 1: Check for explicit URL parameter
  var params = new URLSearchParams(window.location.search);
  var urlOrigin = params.get('origin');

  if (urlOrigin) {
    origin = urlOrigin;
  } else {
    // Priority 2: Fall back to referrer (if external)
    var referrer = document.referrer;
    if (referrer) {
      try {
        var referrerHost = new URL(referrer).hostname;
        // Only capture if external (not changanuk.com or changaneurope.com)
        if (!referrerHost.includes('changanuk.com') &&
            !referrerHost.includes('changaneurope.com')) {
          origin = referrerHost;
        }
      } catch(e) {
        // Invalid URL, ignore
      }
    }
  }

  // Store the origin (even if empty, to mark as "set")
  sessionStorage.setItem('changan_origin', origin);
  sessionStorage.setItem('changan_origin_set', 'true');
})();
```

### LaunchVox Implements (Website)

When submitting to ESS API, read the origin value:

```javascript
// Get the origin value (returns empty string if not set)
var origin = sessionStorage.getItem('changan_origin') || '';
```

### Origin Value Format

| Source | Example Value | Notes |
|--------|---------------|-------|
| URL parameter | `haymarket` | Exactly as provided in `?origin=` |
| Referrer | `haymarket.com` | Domain only (no path/protocol) |
| Direct | `` | Empty string |

---

## Part 2: Form Submission DataLayer

### Form Mapping Table

| Web Form | Cluesourcesecond | Cluesourcethird |
|----------|------------------|-----------------|
| Keep Me Informed | Official Website-Online | Keep Me Informed |
| Test Drive | Official Website-Online | Test Drive |
| Ask For Quotation | Official Website-Online | Ask For Quotation |

### LaunchVox Implements (Website)

Push to dataLayer when a form is successfully submitted:

```javascript
// Call this function when form submission is successful
function trackFormSubmission(formName) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    'event': 'form_submission',
    'form': {
      'name': formName,                    // 'Keep Me Informed', 'Test Drive', or 'Ask For Quotation'
      'page': window.location.pathname     // e.g., '/test-drive'
    },
    'lead': {
      'cluesourcesecond': 'Official Website-Online',
      'cluesourcethird': formName,
      'origin': sessionStorage.getItem('changan_origin') || ''
    }
  });
}
```

### Example Usage

```javascript
// Keep Me Informed form
document.getElementById('kmi-form').addEventListener('submit', function(e) {
  // ... existing form handling code ...

  // After successful submission to ESS API:
  trackFormSubmission('Keep Me Informed');
});

// Test Drive form
document.getElementById('test-drive-form').addEventListener('submit', function(e) {
  // ... existing form handling code ...

  // After successful submission to ESS API:
  trackFormSubmission('Test Drive');
});

// Ask For Quotation form
document.getElementById('quote-form').addEventListener('submit', function(e) {
  // ... existing form handling code ...

  // After successful submission to ESS API:
  trackFormSubmission('Ask For Quotation');
});
```

---

## Part 3: ESS API Integration

### LaunchVox Implements (Website)

When submitting lead data to the ESS API, include these additional fields:

```javascript
// Example ESS API payload
var essPayload = {
  // ... existing form fields (name, email, phone, etc.) ...

  // Required tracking fields:
  'Cluesourcesecond': 'Official Website-Online',
  'Cluesourcethird': formName,  // 'Keep Me Informed', 'Test Drive', or 'Ask For Quotation'
  'origin': sessionStorage.getItem('changan_origin') || ''
};

// Submit to ESS API
fetch('https://ess-api-endpoint.com/leads', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(essPayload)
});
```

---

## Part 4: GTM Configuration

### Alchemy Implements (GTM)

#### Variables to Create

| Variable Name | Type | Configuration |
|---------------|------|---------------|
| `DLV - event` | Data Layer Variable | Data Layer Variable Name: `event` |
| `DLV - form.name` | Data Layer Variable | Data Layer Variable Name: `form.name` |
| `DLV - form.page` | Data Layer Variable | Data Layer Variable Name: `form.page` |
| `DLV - lead.cluesourcesecond` | Data Layer Variable | Data Layer Variable Name: `lead.cluesourcesecond` |
| `DLV - lead.cluesourcethird` | Data Layer Variable | Data Layer Variable Name: `lead.cluesourcethird` |
| `DLV - lead.origin` | Data Layer Variable | Data Layer Variable Name: `lead.origin` |
| `URL Query - origin` | URL Variable | Component: Query, Key: `origin` |

#### Trigger to Create

| Trigger Name | Type | Configuration |
|--------------|------|---------------|
| `CE - Form Submission` | Custom Event | Event name equals `form_submission` |

#### Tags to Create

| Tag Name | Type | Configuration |
|----------|------|---------------|
| `GA4 - Form Submission` | GA4 Event | Event: `generate_lead`, Parameters: form_name, form_page, cluesourcesecond, cluesourcethird, origin |
| `Origin Capture` | Custom HTML | Stores origin param in sessionStorage (fires on All Pages) |

---

## Testing Checklist

### LaunchVox Testing

- [ ] DataLayer push fires on Keep Me Informed form submission
- [ ] DataLayer push fires on Test Drive form submission
- [ ] DataLayer push fires on Ask For Quotation form submission
- [ ] ESS API receives correct `Cluesourcesecond` value
- [ ] ESS API receives correct `Cluesourcethird` value
- [ ] ESS API receives `origin` value when present

### Alchemy Testing

- [ ] Origin captured from URL parameter `?origin=test`
- [ ] Origin captured from external referrer (e.g., come from google.com)
- [ ] Origin NOT overwritten on internal navigation
- [ ] Origin persists in sessionStorage across page navigation
- [ ] GA4 receives `generate_lead` event with all parameters
- [ ] Custom dimension `origin` populated in GA4 reports

### End-to-End Testing

**Test 1: Tagged URL (explicit origin)**
1. Visit `https://www.changanuk.com/?origin=haymarket`
2. Navigate to a form page
3. Submit the form
4. Verify origin = `haymarket`

**Test 2: Untagged external referrer**
1. Click a link from an external site (or simulate with referrer)
2. Navigate to a form page
3. Submit the form
4. Verify origin = referrer domain (e.g., `google.com`)

**Test 3: Direct traffic**
1. Type `https://www.changanuk.com/` directly in browser
2. Navigate to a form page
3. Submit the form
4. Verify origin = `` (empty string)

**Verification Points:**
- GA4 DebugView: Event `generate_lead` with correct `origin` parameter
- ESS API logs: `origin` field populated correctly
- sessionStorage: `changan_origin` value persists across pages

---

## DataLayer Schema Reference

```json
{
  "event": "form_submission",
  "form": {
    "name": "string",
    "page": "string"
  },
  "lead": {
    "cluesourcesecond": "string",
    "cluesourcethird": "string",
    "origin": "string"
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event` | string | Yes | Always "form_submission" |
| `form.name` | string | Yes | One of: "Keep Me Informed", "Test Drive", "Ask For Quotation" |
| `form.page` | string | Yes | Page path where form was submitted |
| `lead.cluesourcesecond` | string | Yes | Always "Official Website-Online" |
| `lead.cluesourcethird` | string | Yes | Same as form.name |
| `lead.origin` | string | No | Value from `?origin=` URL parameter, empty string if not present |

---

## Questions / Clarifications

Please contact:
- **GTM / Analytics:** Alchemy
- **Website Implementation:** LaunchVox

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-28 | Alchemy | Initial specification |
