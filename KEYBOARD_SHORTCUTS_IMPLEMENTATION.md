# Keyboard Shortcuts Implementation Guide

## Overview
This implementation adds power-user keyboard shortcuts to the CKCIAS Drought Monitor application, allowing users to quickly navigate and interact with the application without using their mouse.

## Files Created

### 1. `/hooks/useKeyboardShortcuts.ts`
Custom React hook that manages keyboard event listeners and prevents shortcuts from triggering when typing in input fields.

**Features:**
- Automatic detection of input fields (input, textarea, select, contentEditable)
- Configurable shortcuts with custom actions
- Optional preventDefault control
- Enable/disable functionality

**Usage:**
```typescript
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

useKeyboardShortcuts({
  shortcuts: [
    {
      key: 'r',
      description: 'Refresh data',
      action: () => handleRefresh()
    }
  ],
  enabled: true // optional, defaults to true
});
```

### 2. `/components/ShortcutsHelpModal.tsx`
Beautiful modal component that displays all available keyboard shortcuts.

**Features:**
- Clean, modern design matching the app's aesthetic
- Organized shortcuts by category (Actions, Navigation, Help)
- Icon representation for each shortcut key
- Dismissible with Escape key or click outside
- Prevents body scroll when open
- Smooth animations

**Props:**
```typescript
interface ShortcutsHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

### 3. Updated `/components/RegionSearch.tsx`
Enhanced RegionSearch component with imperative ref methods.

**New Features:**
- `forwardRef` implementation for parent component access
- `focus()` method - programmatically focus the search input
- `clear()` method - clear search and reset state
- Exported `RegionSearchRef` interface for type safety

**Interface:**
```typescript
export interface RegionSearchRef {
  focus: () => void;
  clear: () => void;
}
```

### 4. Updated `/App.tsx`
Main application file with integrated keyboard shortcuts.

**Changes:**
- Added `useRef` hook for RegionSearch component
- Integrated `useKeyboardShortcuts` hook
- Added state for shortcuts help modal
- Added keyboard shortcuts button in header
- Connected ref to RegionSearch component

### 5. `/index.css`
Global stylesheet with custom animations.

**Includes:**
- Tailwind CSS directives
- `fadeInUp` animation for smooth modal entrance
- Custom scrollbar styles

## Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| `R` | Refresh Data | Manually triggers data refresh for all regions |
| `/` | Focus Search | Moves cursor to region search input field |
| `Esc` | Clear/Close | Clears search and closes selected region panel |
| `?` | Show Help | Opens keyboard shortcuts help modal |

## How It Works

### Shortcut Detection Flow
1. User presses a key
2. `useKeyboardShortcuts` hook captures the keydown event
3. Hook checks if user is typing in an input field
4. If not typing, hook looks for matching shortcut
5. Matching shortcut's action is executed
6. Event is prevented (unless configured otherwise)

### Preventing Conflicts
The implementation automatically prevents shortcuts from triggering when:
- User is typing in `<input>` elements
- User is typing in `<textarea>` elements
- User is typing in `<select>` dropdowns
- User is in `contentEditable` elements

### Special Cases
- **Escape key:** Does not prevent default to allow normal browser behavior
- **Refresh shortcut:** Checks if refresh is already in progress before triggering
- **Focus search:** Uses imperative ref to focus the input programmatically

## Integration Steps

### Step 1: Import Required Dependencies
```typescript
import { useRef } from 'react';
import RegionSearch, { RegionSearchRef } from './components/RegionSearch';
import ShortcutsHelpModal from './components/ShortcutsHelpModal';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
```

### Step 2: Create State and Refs
```typescript
const [showShortcutsModal, setShowShortcutsModal] = useState(false);
const regionSearchRef = useRef<RegionSearchRef>(null);
```

### Step 3: Configure Keyboard Shortcuts
```typescript
useKeyboardShortcuts({
  shortcuts: [
    {
      key: 'r',
      description: 'Refresh data',
      action: () => {
        if (!isRefreshing) {
          handleManualRefresh();
        }
      }
    },
    {
      key: '/',
      description: 'Focus search',
      action: () => {
        regionSearchRef.current?.focus();
      }
    },
    {
      key: 'Escape',
      description: 'Clear search',
      action: () => {
        regionSearchRef.current?.clear();
        setSelectedRegionData(null);
      },
      preventDefault: false
    },
    {
      key: '?',
      description: 'Show shortcuts',
      action: () => {
        setShowShortcutsModal(true);
      }
    }
  ]
});
```

### Step 4: Add UI Elements
```tsx
{/* Header hint button */}
<button
  onClick={() => setShowShortcutsModal(true)}
  className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors group"
  title="View keyboard shortcuts"
>
  <svg className="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
  </svg>
  <span className="hidden sm:inline">Keyboard shortcuts: Press</span>
  <kbd className="px-1.5 py-0.5 text-xs font-semibold text-slate-700 bg-slate-100 border border-slate-300 rounded shadow-sm group-hover:bg-white">?</kbd>
</button>

{/* Modal */}
<ShortcutsHelpModal
  isOpen={showShortcutsModal}
  onClose={() => setShowShortcutsModal(false)}
/>

{/* Region Search with ref */}
<RegionSearch
  ref={regionSearchRef}
  regions={NZ_REGIONS}
  onRegionSelect={handleRegionSearchSelect}
/>
```

## Customization

### Adding New Shortcuts
To add a new keyboard shortcut:

1. Add the shortcut to the `useKeyboardShortcuts` configuration in `App.tsx`:
```typescript
{
  key: 'h', // The key to listen for
  description: 'Go to home',
  action: () => {
    // Your action here
  },
  preventDefault: true // optional, defaults to true
}
```

2. Update the `ShortcutsHelpModal.tsx` shortcuts array:
```typescript
{
  key: 'H',
  description: 'Go to home',
  category: 'Navigation' // or 'Actions', 'Help'
}
```

3. Add an icon for the key in `getKeyIcon()` function if desired.

### Modifying the Help Modal
The help modal is fully customizable. You can:
- Change colors by modifying Tailwind classes
- Add/remove categories
- Customize icons
- Adjust animations
- Modify layout

### Disabling Shortcuts
To temporarily disable shortcuts:
```typescript
useKeyboardShortcuts({
  shortcuts: [...],
  enabled: false
});
```

## Design Decisions

### Why Not Use a Library?
- Custom implementation provides full control
- Lightweight - no additional dependencies
- Tailored specifically to app needs
- Easy to understand and maintain

### Why These Specific Keys?
- `R` - Common convention for refresh
- `/` - Industry standard for search (GitHub, Slack, etc.)
- `Esc` - Universal close/cancel action
- `?` - Common convention for help/shortcuts

### UX Considerations
- Shortcuts only work when not typing (prevents conflicts)
- Visual hint in header (discoverability)
- Help modal shows all shortcuts (learnability)
- Non-modal shortcuts don't interrupt workflow

## Browser Compatibility
The implementation uses standard browser APIs:
- `addEventListener('keydown')` - Full browser support
- `useEffect` and `useCallback` - React standard hooks
- No browser-specific features

Tested on:
- Chrome/Edge (Chromium)
- Firefox
- Safari

## Accessibility
- Modal is keyboard accessible (Escape to close)
- Focus management in RegionSearch
- ARIA labels on buttons
- Clear visual feedback

## Performance
- Event listeners are properly cleaned up
- Callbacks are memoized with `useCallback`
- No memory leaks
- Minimal re-renders

## Future Enhancements
Potential additions:
- Command palette (Cmd/Ctrl + K)
- Sequence shortcuts (e.g., 'g' then 'h' for home)
- Customizable shortcuts (user preferences)
- Shortcuts for map navigation
- Export/import shortcuts configuration

## Troubleshooting

### Shortcuts Not Working
1. Check browser console for errors
2. Verify `useKeyboardShortcuts` hook is called
3. Ensure shortcuts are enabled (`enabled: true`)
4. Check if typing in an input field

### Modal Not Appearing
1. Verify `showShortcutsModal` state is set to `true`
2. Check z-index conflicts
3. Ensure modal is rendered in DOM

### RegionSearch Focus Not Working
1. Verify ref is properly attached to RegionSearch
2. Check `forwardRef` implementation
3. Ensure `useImperativeHandle` is configured

## Testing
To test the implementation:
1. Press `?` - Help modal should appear
2. Press `Esc` - Modal should close
3. Press `/` - Search should focus
4. Type in search - Other shortcuts should not trigger
5. Press `R` - Data should refresh

## Conclusion
This implementation provides a professional, accessible, and performant keyboard shortcuts system for power users while maintaining a clean, maintainable codebase.
