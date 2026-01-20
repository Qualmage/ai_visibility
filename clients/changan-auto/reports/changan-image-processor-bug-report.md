# Changan Europe - Image Processor Bug Report

**Date:** January 13, 2026
**Prepared by:** Analytics Team
**Status:** Active Issue - Requires Developer Action

---

## Executive Summary (For Business Stakeholders)

### What's Happening?
Google is having trouble crawling some images on the Changan Europe website. When Google tries to access certain vehicle images, the website returns an error instead of the image. This has been happening since early December 2025.

### Why Does This Matter?
- **SEO Impact:** Google may remove affected images from search results
- **User Experience:** Some users may see broken images or slow loading pages
- **Brand Perception:** Error pages look unprofessional if users encounter them

### What's NOT Broken?
- The main website pages are working
- Most images load correctly for regular visitors
- The configurator tool is functional

### What IS Broken?
- **Two specific S07 vehicle images** fail when resized to 1920x960 pixels
- These images likely have unusual properties (color profile, metadata, etc.)
- This affects vehicle gallery images that Google is trying to index

### The Good News
- The issue is isolated to **only 2 specific images** (not a system-wide problem)
- Regular website visitors rarely encounter this error (they get cached versions)
- The fix is likely simple: **re-export or replace the two problematic images**

---

## Technical Summary (For Developers)

### Issue Description
The DNN ImageProcessor module throws a 500 Internal Server Error when processing images with specific resize parameters (`w=1920&h=960`). Other resize dimensions work correctly.

### Affected System
- **Platform:** IIS / ASP.NET (.NET Framework)
- **CMS:** DNN (DotNetNuke)
- **Module:** Adam (Asset Digital Asset Management)
- **Image Processor:** On-the-fly resizer (likely ImageProcessor library)
- **CDN:** Alibaba Cloud CDN (Tengine)

### Error Timeline
| Date | Event |
|------|-------|
| Dec 5, 2025 | First errors appear, 43,022ms avg response time (timeout) |
| Dec 13, 2025 | Errors become consistent (2-4/day) |
| Dec 23-26, 2025 | Spike to 13-29 errors/day |
| Jan 11, 2026 | 28 errors recorded |
| Ongoing | ~10-28 errors per day |

### Root Cause Analysis
1. **NOT a CDN issue** - Alibaba CDN is correctly:
   - Serving cached content (cache HITs work)
   - NOT caching error responses
   - Passing requests through to origin on cache MISS

2. **NOT a dimension issue** - The 1920x960 resize works on other images:
   - `DJI_0600.jpg?w=1920&h=960` - **Works (200 OK)**
   - `3-S07-Black-roof.png?w=1920&h=960` - **FAILS (500 Error)**

3. **The issue is IMAGE-SPECIFIC** - Only these two S07 images fail:
   - `3-S07-Black-roof.png`
   - `2-S07-Black-Back.png`

4. **Likely cause: Source image properties** - These PNGs may have:
   - Unusual color profile (CMYK, wide gamut)
   - Corrupted or malformed metadata
   - Very large dimensions or file size
   - Unsupported bit depth or transparency mode
   - Embedded ICC profile the image processor can't handle

---

## How to Reproduce the Error

### Method 1: Direct URL (Simplest)

Open this URL in any browser:

```
https://www.changaneurope.com/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&h=960&quality=75&mode=crop&scale=both
```

**Expected Result:** Yellow "Runtime Error" page (ASP.NET error)

### Method 2: Compare Working vs Failing

**This URL WORKS (no height param):**
```
https://www.changaneurope.com/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&quality=75&mode=crop&scale=both
```

**This URL FAILS (with height=960):**
```
https://www.changaneurope.com/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&h=960&quality=75&mode=crop&scale=both
```

### Method 3: Using cURL

```bash
# This will return a 500 error
curl -I "https://www.changaneurope.com/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&h=960&quality=75&mode=crop&scale=both"
```

**Response Headers (showing CDN passed error through):**
```
HTTP/2 500
server: Tengine
x-cache: MISS TCP_MISS
x-swift-error: orig response 5xx error
content-type: text/html; charset=utf-8
```

### Method 4: Chrome DevTools

1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Navigate to the failing URL above
4. Observe:
   - Status: **500**
   - Response: ASP.NET Runtime Error page

---

## Evidence from Live Testing

### Test 1: Failing Image Request

**Request:**
```
GET /Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&h=960&quality=75&mode=crop&scale=both
```

**Response Headers:**
| Header | Value | Meaning |
|--------|-------|---------|
| `status` | 500 | Server error |
| `server` | Tengine | Alibaba CDN edge |
| `x-cache` | MISS TCP_MISS | Not from cache, hit origin |
| `x-swift-error` | orig response 5xx error | CDN confirms origin failed |
| `x-swift-cachetime` | 0 | Error not cached (correct) |
| `content-type` | text/html | Error page, not image |

**Response Body:**
```html
<H1>Server Error in '/' Application.</H1>
<h2><i>Runtime Error</i></h2>
<b>Description:</b> An application error occurred on the server...
```

### Test 2: Working Image Request (Same Image, Different Params)

**Request:**
```
GET /Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&quality=75&mode=crop&scale=both
```

**Response Headers:**
| Header | Value | Meaning |
|--------|-------|---------|
| `status` | 200 | Success |
| `x-cache` | HIT TCP_MEM_HIT | Served from CDN cache |
| `content-type` | image/png | Correct image response |

### Test 3: Proof That 1920x960 Works on Other Images

**Working image (different source):**
```
https://www.changaneurope.com/Portals/3/adam/ContentBlocks/cr4J-vaEm0OhKLYJQMMtaA/Image/DJI_0600.jpg?w=1920&h=960&quality=75&mode=crop&scale=both
```
**Result:** 200 OK - Image loads correctly at 1920x960

**Failing image (S07 vehicle):**
```
https://www.changaneurope.com/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&h=960&quality=75&mode=crop&scale=both
```
**Result:** 500 Error - Runtime Error page

**Conclusion:** The 1920x960 dimension is NOT the problem. The two S07 source images have something the image processor cannot handle.

### Test 4: Configurator Page

**URL:** `https://www.changaneurope.com/uk/configurator`

**Result:** All 92 requests successful (200 OK)

**Image requests on configurator use different dimensions:**
- `?w=1920&quality=75` (no height)
- `?w=1230&h=307&quality=75`

These work because they don't trigger the broken 1920x960 resize path.

---

## Google Search Console Data

### Crawl Error Statistics (Last 90 Days)
- **Total failed crawl requests:** 339
- **Total download size:** 1.46M bytes
- **Average response time:** 1,610 ms

### Error Distribution by URL Type

| URL Type | Count | % of Total | First Occurrence |
|----------|-------|------------|------------------|
| Image resize (1920x960) | 64 | 91% | Dec 13, 2025 |
| Country homepages (/gr, /nl) | 2 | 3% | Dec 5, 2025 |
| UK S07 Model Page | 1 | 1% | Oct 30, 2025 |
| Spanish Auth Page | 1 | 1% | Dec 6, 2025 |
| Homepage | 1 | 1% | Jan 2, 2026 |
| **Total** | **70** | **100%** | |

### Failing Image URLs (All Same Pattern)
Only **two images** account for all 64 image resize errors:
```
/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&h=960&quality=75&mode=crop&scale=both
/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/2-S07-Black-Back.png?w=1920&h=960&quality=75&mode=crop&scale=both
```

### Page-Level 5XX Errors (Potential Cascade Effect)
These page errors may indicate the image processor failures are causing broader server instability:

| Date | Time | URL | Notes |
|------|------|-----|-------|
| Oct 30, 2025 | 5:38 AM | `/uk/models/changan-deepal-s07/` | First S07 page error (before image errors began) |
| Dec 5, 2025 | 4:03 PM | `/gr` | Greek homepage down |
| Dec 5, 2025 | 4:03 PM | `/nl` | Dutch homepage down |
| Dec 6, 2025 | 1:13 AM | `/es/user-authentication?returnurl=/es/configurador/deepal-s05` | Spanish configurator auth |
| Jan 2, 2026 | 11:16 AM | `/` | Main homepage 5XX |

---

## CDN Behavior Explained

### Why Regular Users Don't See the Error

```
User Request
     |
     v
[Alibaba CDN Edge]
     |
     |-- Cache HIT? --> Return cached image (works!)
     |
     |-- Cache MISS? --> Forward to Origin Server
                              |
                              v
                    [DNN Image Processor]
                              |
                              |-- 1920x960? --> CRASH (500 Error)
                              |
                              |-- Other size? --> Return resized image
```

**Key Points:**
1. CDN has long cache times (30 days / 1 year max-age)
2. Most images were cached BEFORE the bug was introduced
3. Cache HITs return old working images
4. Only cache MISSes expose the broken origin
5. Googlebot often bypasses/ignores cache, so it sees the errors

---

## Recommended Actions

### Immediate (Developer)

1. **Enable detailed errors temporarily** to get the stack trace:
   ```xml
   <!-- web.config -->
   <configuration>
       <system.web>
           <customErrors mode="Off"/>
       </system.web>
   </configuration>
   ```
   **Remember to revert after debugging!**

2. **Check IIS/Application logs** for exceptions around:
   - Dec 5, 2025 (first occurrence)
   - Any time in the last 24 hours

3. **Review ImageProcessor configuration** for:
   - Memory limits
   - Max dimensions settings
   - Timeout values

4. **Test the specific image** (`3-S07-Black-roof.png`) locally:
   - Does it have unusual properties? (Color space, bit depth, size)
   - Can it be resized to 1920x960 manually?

### Investigation Questions

1. **What's special about these two source images?** Check:
   - File size (are they unusually large?)
   - Dimensions of the original (very high resolution?)
   - Color profile (sRGB, Adobe RGB, ProPhoto, CMYK?)
   - Bit depth (8-bit, 16-bit, 32-bit?)
   - Transparency/alpha channel settings
   - ICC profile embedded in the PNG
2. Were these images **uploaded or modified** around Dec 5, 2025?
3. Can you **re-export these images** from the original source with standard settings?
4. Do these images **open correctly** in image editing software?

### Potential Fixes

| Approach | Description | Recommended |
|----------|-------------|-------------|
| **Re-export source images** | Open in Photoshop/GIMP, save as standard sRGB PNG | ✅ Try first |
| **Replace the images** | Upload new versions with standard color profile | ✅ Quick fix |
| **Update ImageProcessor** | Check for library updates that handle edge cases | Maybe |
| **Add error handling** | Graceful fallback to original image instead of 500 | Good practice |
| **Pre-generate sizes** | Create 1920x960 versions offline, serve statically | Workaround |

---

## Files and Resources

### Google Search Console Export
- `Chart.csv` - Daily error counts and response times
- `Table.csv` - Individual failing URLs with timestamps
- Location: `clients/changan-auto/crawl-stats-extracted/`

### Previous Investigation
- `changan-server-error-investigation.md` - Initial analysis

### Useful Links
- [Google Search Console](https://search.google.com/search-console) - Crawl stats
- [Alibaba CDN Docs](https://www.alibabacloud.com/help/en/cdn) - CDN behavior reference

---

## Appendix: Full Response Headers from Failed Request

```
HTTP/2 500
ali-swift-global-savetime: 1768334997
cache-control: private
connection: keep-alive
content-length: 3490
content-type: text/html; charset=utf-8
date: Tue, 13 Jan 2026 20:09:57 GMT
eagleid: a3b5f39f17683349974638410e
server: Tengine
timing-allow-origin: *
via: ens-cache17.l2de4[121,121,500-1281,M], ens-cache17.l2de4[122,0], ens-cache21.gb9[141,140,500-1281,M], ens-cache11.gb9[172,141,0]
x-cache: MISS TCP_MISS dirn:-2:-2
x-frame-options: SAMEORIGIN
x-swift-cachetime: 0
x-swift-error: orig response 5xx error
x-swift-savetime: Tue, 13 Jan 2026 20:09:57 GMT
x-xss-protection: 1; mode=block
```

---

## Upptime Monitoring Data

### Overview
External uptime monitoring at [ChanganUpptime-v1](https://lv-cmilne.github.io/ChanganUpptime-v1) shows **page-level 404 errors** occurring intermittently. These are separate from but potentially related to the image processor 500 errors.

### Key Distinction
| Error Type | Source | HTTP Code | Affects |
|------------|--------|-----------|---------|
| Image processor errors | Google Search Console | **500** | Image URLs with 1920x960 resize |
| Page-level errors | Upptime Monitoring | **404** | Full pages (test-drive, privacy policy, etc.) |

### Recent Page Outages (from Upptime)

| Date | Page | HTTP Code | Duration |
|------|------|-----------|----------|
| Jan 13, 2026 | UK Privacy Policy | 404 | 19 min |
| Jan 11, 2026 | UK Book a Test Drive | 404 | 19 min |

### Possible Correlation

The page-level 404 errors may be caused by:

1. **DNN routing failure** - When the image processor crashes, it may corrupt the application state, causing DNN to fail to route subsequent requests
2. **App pool recycling** - 500 errors may trigger IIS app pool recycling, during which pages return 404
3. **CDN origin failure** - If the origin returns 500 multiple times, the CDN may start returning 404 for the page
4. **Separate issue** - The 404s could be an unrelated CMS configuration problem

### Recommendation

When investigating the image processor 500 errors, also check:
- IIS Application Pool settings (recycling behavior)
- DNN error logs around the times of the 404 outages
- Whether pages that went down contain the failing 1920x960 image URLs

---

## Contact

For questions about this report, contact the Analytics Team.

**Report Generated:** January 13, 2026
