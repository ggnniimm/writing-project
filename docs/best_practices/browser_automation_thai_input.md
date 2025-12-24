# Best Practice: Browser Automation for Thai Input

**Problem:** `browser_press_key` and standard typing simulation tools often fail with Thai characters (and other non-ASCII text) due to keyboard layout mapping issues or driver limitations.

**Solution:** Always use `execute_browser_javascript` to set values for input fields when dealing with Thai text.

## Bad Pattern
```json
{
  "tool": "browser_press_key",
  "text": "อ. 123/2567"
}
```
*Risk:* Throws "Unknown key" errors or produces garbled text.

## Good Pattern
```javascript
(function() {
  const input = document.querySelector('input#redCase');
  input.value = 'อ. 123/2567';
  // Trigger events if necessary (React/Vue/Angular sometimes need this)
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  return true;
})()
```

## Specific to Administrative Court Search
For `https://www.admincourt.go.th/admincourt/site/05SearchSuit.html`:

1.  Use **JavaScript** to populate the Red Number fields directly.
2.  Clear the Black Number fields (often pre-filled or focused) to avoid ambiguity.
3.  Click Search.

```javascript
/* Preferred method for "Red Case อ. 674/2557" */
(function() {
  const inputs = document.querySelectorAll('input.form-control');
  // Clear any Black Case inputs (indices 5, 6 usually)
  inputs[5].value = ''; 
  inputs[6].value = '';
  // Set Red Case inputs (indices 7, 8 usually)
  inputs[7].value = '674'; // Number only, if 'court' dropdown handles type, OR 'อ. 674' if text field
  inputs[8].value = '2557'; // Year
  return true;
})()
```
