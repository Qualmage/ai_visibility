# Changan Europe Website - Server Error Investigation

## Date: January 13, 2026

---

## Issue 1: IIS Server Error Page

### User Provided Screenshot
The user shared a screenshot of a classic **ASP.NET/IIS Runtime Error page** (Yellow Screen of Death).

### Analysis
- **"Server Error in '/' Application"** — standard IIS error header
- **"Runtime Error"** — indicates an unhandled exception in the ASP.NET application
- **`<customErrors>` configuration snippets** — specific to ASP.NET's `web.config` file
- **Yellow background with code blocks** — signature styling of ASP.NET error pages

The page indicates that detailed error information is hidden from remote users (security feature), and shows how to:
1. Expose full error details by setting `customErrors mode="Off"`
2. Redirect to a custom error page using `mode="RemoteOnly"` with a `defaultRedirect`

**Platform:** IIS with ASP.NET runtime (likely .NET Framework)

---

## Issue 2: Google Search Console - 5XX Server Errors

### User Provided Data

**Server Connectivity Report:**
- High fail rate reported last week
- Failed crawl requests increasing since mid-December 2025

**Crawl Requests: Server Error (5XX) Details:**
- **Total crawl requests:** 339
- **Total download size:** 1.46M bytes
- **Average response time:** 1.61K ms (1,610 ms - quite slow)

### Failing URL Pattern
All failing URLs follow this pattern:
```
https://www.changaneurope.com/Portals/0/adam/VehicleManagement/[hash]/Images/[filename].png?w=1920&h=960&quality=75&mode=crop&scale=both
```

### Example Failing URLs (from Jan 11, 2026):
1. `/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/3-S07-Black-roof.png?w=1920&h=960&quality=75&mode=crop&scale=both`
2. `/Portals/0/adam/VehicleManagement/ItuoPcj3nkK9PJqrplTUdg/Images/2-S07-Black-Back.png?w=1920&h=960&quality=75&mode=crop&scale=both`

### Timeline
- Errors started: Early December 2025
- Trend: Steadily increasing
- Peak: ~25-30 failed crawl requests per day in late December/early January 2026

---

## Root Cause Analysis

### What the Data Tells Us

1. **Image resizing/processing module is failing** under load or has a bug
2. The `adam` path indicates **DNN (DotNetNuke) Adam (Asset Digital Asset Management)** module
3. Query parameters (`w=`, `h=`, `quality=`, `mode=`, `scale=`) indicate **on-the-fly image resizer** — likely **ImageProcessor** or similar
4. The 1.61K ms average response time suggests server is struggling

### Likely Causes

1. **Memory pressure** from image processing operations
2. **Bug introduced** in a December update/deployment
3. **Disk I/O issues** or temp folder permissions
4. **Image processing library** hitting unhandled exception on certain images

---

## Affected Page

**URL:** `https://www.changaneurope.com/uk/models/changan-deepal-s07/test-drive`

This configurator page is going down, likely because:
1. Underlying image/asset processing is broken
2. When the page tries to load dynamically resized vehicle images, the server throws a 500 error
3. DNN Adam module handling vehicle assets has an issue
4. Critical asset failures cause the page to error out entirely

---

## Recommended Investigation Steps

### Immediate Actions

1. **Check IIS/application logs** for specific exception details around the failing timestamps
2. **Review deployments/updates** made in late November/early December 2025
3. **Monitor server resources** — check if memory or CPU spikes correlate with errors
4. **Test failing URLs directly** to reproduce the error

### Enable Detailed Errors (Temporarily)

In `web.config`, set:
```xml
<configuration>
    <system.web>
        <customErrors mode="Off"/>
    </system.web>
</configuration>
```

This will expose the actual stack trace to pinpoint the exact cause.

**⚠️ Remember to revert this after debugging — don't leave detailed errors exposed in production!**

---

## Chrome DevTools Instructions for Detecting Failing Image URLs

### Method 1: Network Tab (Recommended)

1. **Open DevTools**: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
2. **Go to the Network tab**
3. **Filter by images**: Click the **Img** filter button in the toolbar
4. **Enable "Preserve log"**: Check this box so requests persist across page navigations
5. **Load the page**: Navigate to `https://www.changaneurope.com/uk/models/changan-deepal-s07/test-drive`
6. **Look for red entries**: Failed requests (5XX, 4XX) appear in red
7. **Filter for errors**: Right-click column headers → ensure **Status** is visible, then sort by Status, or use filter: `status-code:500` or `is:from-cache:false`

### Method 2: Console Tab

1. Open DevTools → **Console** tab
2. Load the page
3. Look for red error messages like:
   ```
   Failed to load resource: the server responded with a status of 500 ()
   ```
4. These will show the full URLs that failed

### Method 3: Filter for Specific Path

In the Network tab filter box, type:
```
/adam/VehicleManagement/
```

This filters to show only requests matching the problematic image URLs.

### Capturing Failed Requests

When you find failing requests:
- Right-click → **Copy** → **Copy as cURL** — gives you a testable command
- Right-click → **Copy** → **Copy URL** — gives you the exact URL

---

## Information Still Needed

1. **Exact error message** when visiting the configurator page (screenshot or text)
2. **IIS logs** or **DNN Event Viewer logs** from around the time of failures
3. Confirmation whether **other model pages** (not just S07) are also affected
4. **Stack trace** from enabling `customErrors mode="Off"`

---

## Technical Summary

| Component | Details |
|-----------|---------|
| **Platform** | IIS / ASP.NET (likely .NET Framework) |
| **CMS** | DNN (DotNetNuke) |
| **Asset Management** | DNN Adam module |
| **Image Processing** | On-the-fly resizer (likely ImageProcessor) |
| **Error Type** | 5XX Server Errors |
| **Affected URLs** | `/Portals/0/adam/VehicleManagement/*/Images/*.png` |
| **Query Params** | `w`, `h`, `quality`, `mode`, `scale` (image resize params) |
| **Start Date** | Early December 2025 |
| **Trend** | Increasing |
| **Avg Response Time** | 1,610 ms (slow) |

---

## Next Steps for Claude Code

1. Analyze IIS logs for 500 errors matching the URL pattern
2. Search for exceptions in DNN Event Viewer
3. Check ImageProcessor or image resizing module configuration
4. Review any code changes or deployments from late November/early December
5. Test image processing with specific failing image files
6. Check server memory and disk space during peak error times
