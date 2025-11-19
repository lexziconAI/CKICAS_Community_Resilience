# Keyboard Shortcuts - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser Window                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    User Interaction                        │ │
│  │                                                            │ │
│  │        User Presses Key (e.g., 'R', '/', 'Esc', '?')     │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                       │
│                         ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │           useKeyboardShortcuts Hook                       │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  1. Capture keydown event                          │ │ │
│  │  │  2. Check if typing in input field                 │ │ │
│  │  │  3. Match key to registered shortcuts              │ │ │
│  │  │  4. Execute action if match found                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                       │
│         ┌───────────────┼───────────────┐                       │
│         │               │               │                       │
│         ▼               ▼               ▼                       │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────┐            │
│  │ Refresh  │   │ Focus Search │   │ Show Modal  │            │
│  │  Action  │   │    Action    │   │   Action    │            │
│  └────┬─────┘   └──────┬───────┘   └──────┬──────┘            │
│       │                │                   │                   │
│       ▼                ▼                   ▼                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                     App.tsx                             │  │
│  │  ┌───────────────────────────────────────────────────┐ │  │
│  │  │  handleManualRefresh()                           │ │  │
│  │  │  regionSearchRef.current?.focus()                │ │  │
│  │  │  setShowShortcutsModal(true)                     │ │  │
│  │  └───────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
App (Root Component)
│
├─── useKeyboardShortcuts (Hook)
│    ├─── Window Event Listener (keydown)
│    └─── Shortcut Registry
│         ├─── 'r' → handleManualRefresh()
│         ├─── '/' → regionSearchRef.current?.focus()
│         ├─── 'Escape' → clear() + setSelectedRegionData(null)
│         └─── '?' → setShowShortcutsModal(true)
│
├─── Header
│    └─── Keyboard Shortcuts Button
│         └─── onClick: setShowShortcutsModal(true)
│
├─── RegionSearch (forwardRef)
│    ├─── ref: regionSearchRef
│    └─── Exposed Methods:
│         ├─── focus()
│         └─── clear()
│
└─── ShortcutsHelpModal
     ├─── isOpen: showShortcutsModal
     ├─── onClose: () => setShowShortcutsModal(false)
     └─── Content:
          ├─── Actions Category
          ├─── Navigation Category
          └─── Help Category
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Keyboard Event Flow                      │
└─────────────────────────────────────────────────────────────┘

User Presses Key
      │
      ▼
┌─────────────────────────────────────┐
│   Browser Keydown Event             │
│   event.key = 'r' (example)         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  useKeyboardShortcuts Hook          │
│  handleKeyPress(event)              │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐     NO
│  Is user typing in input?           │ ──────► Continue
│  (INPUT/TEXTAREA/SELECT check)      │
└────────────┬────────────────────────┘
             │ YES
             ▼
         Return (ignore)


┌─────────────────────────────────────┐
│  Find matching shortcut             │
│  shortcuts.find(s => s.key === 'r') │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐    NO MATCH
│  Shortcut found?                    │ ──────────► Return
└────────────┬────────────────────────┘
             │ YES
             ▼
┌─────────────────────────────────────┐
│  event.preventDefault()             │
│  (if not disabled for this shortcut)│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Execute shortcut.action()          │
│  e.g., handleManualRefresh()        │
└─────────────────────────────────────┘
```

## State Management

```
┌──────────────────────────────────────────────────────────┐
│                  App.tsx State                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  showShortcutsModal: boolean                   │    │
│  │  ├─── false (default)                          │    │
│  │  ├─── true (when '?' pressed)                  │    │
│  │  └─── false (when modal closed)                │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  regionSearchRef: RefObject<RegionSearchRef>   │    │
│  │  ├─── .current?.focus()                        │    │
│  │  └─── .current?.clear()                        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  selectedRegionData: DroughtRiskData | null    │    │
│  │  ├─── Set when region selected                 │    │
│  │  └─── Cleared on 'Esc' key                     │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  isRefreshing: boolean                         │    │
│  │  ├─── Prevents duplicate refresh on 'R'        │    │
│  │  └─── Checked before triggering refresh        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Event Listener Lifecycle

```
Component Mount
      │
      ▼
┌─────────────────────────────────────┐
│  useKeyboardShortcuts() called      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  useEffect(() => {                  │
│    window.addEventListener(...)     │
│  }, [handleKeyPress])               │
└────────────┬────────────────────────┘
             │
             ▼
    Event Listener Active
    (Listening for keydown)
             │
             │  User presses keys...
             │  Shortcuts execute...
             │
             ▼
Component Unmount / Dependencies Change
             │
             ▼
┌─────────────────────────────────────┐
│  Cleanup Function                   │
│  window.removeEventListener(...)    │
└─────────────────────────────────────┘
             │
             ▼
    Event Listener Removed
    (No memory leaks)
```

## Modal Interaction Flow

```
User Triggers Modal
(Press '?' OR Click Button)
      │
      ▼
┌─────────────────────────────────────┐
│  setShowShortcutsModal(true)        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  ShortcutsHelpModal Renders         │
│  - Backdrop appears                 │
│  - Modal animates in (fadeInUp)     │
│  - Body scroll locked               │
└────────────┬────────────────────────┘
             │
             ▼
    User Views Shortcuts
             │
             ├─── Press 'Esc'
             ├─── Click outside
             └─── Click "Got it" button
             │
             ▼
┌─────────────────────────────────────┐
│  onClose() called                   │
│  setShowShortcutsModal(false)       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  ShortcutsHelpModal Unmounts        │
│  - Modal fades out                  │
│  - Body scroll restored             │
└─────────────────────────────────────┘
```

## RegionSearch Ref Communication

```
App.tsx
  │
  ├─── const regionSearchRef = useRef<RegionSearchRef>(null)
  │
  └─── <RegionSearch ref={regionSearchRef} ... />
              │
              ▼
        RegionSearch.tsx
              │
              ├─── forwardRef<RegionSearchRef, Props>
              │
              ├─── useImperativeHandle(ref, () => ({
              │      focus: () => inputRef.current?.focus(),
              │      clear: () => handleClear()
              │    }))
              │
              └─── Internal: inputRef → <input ref={inputRef} />

When '/' pressed:
  App.tsx: regionSearchRef.current?.focus()
       │
       ▼
  RegionSearch: inputRef.current?.focus()
       │
       ▼
  Browser: <input> element gains focus

When 'Esc' pressed:
  App.tsx: regionSearchRef.current?.clear()
       │
       ▼
  RegionSearch: handleClear()
       │
       ├─── setSearchTerm('')
       ├─── setIsOpen(false)
       └─── inputRef.current?.focus()
```

## Shortcut Prevention Logic

```
┌─────────────────────────────────────────────────────────┐
│          Shortcut Prevention Decision Tree             │
└─────────────────────────────────────────────────────────┘

Keydown Event
      │
      ▼
┌─────────────────────┐
│ Get event.target    │
└──────┬──────────────┘
       │
       ▼
┌────────────────────────┐      YES
│ Is tagName = 'INPUT'?  │ ────────► PREVENT SHORTCUT
└──────┬─────────────────┘          (User is typing)
       │ NO
       ▼
┌────────────────────────┐      YES
│ Is tagName = 'TEXTAREA'│ ────────► PREVENT SHORTCUT
└──────┬─────────────────┘          (User is typing)
       │ NO
       ▼
┌────────────────────────┐      YES
│ Is tagName = 'SELECT'? │ ────────► PREVENT SHORTCUT
└──────┬─────────────────┘          (User is selecting)
       │ NO
       ▼
┌────────────────────────┐      YES
│ isContentEditable?     │ ────────► PREVENT SHORTCUT
└──────┬─────────────────┘          (User is editing)
       │ NO
       ▼
┌────────────────────────┐      NO
│ enabled = true?        │ ────────► PREVENT SHORTCUT
└──────┬─────────────────┘          (Shortcuts disabled)
       │ YES
       ▼
  ALLOW SHORTCUT
  (Process normally)
```

## Performance Optimization

```
┌──────────────────────────────────────────────────────────┐
│              Performance Optimizations                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. useCallback for handleKeyPress                      │
│     ├─── Prevents unnecessary re-renders                │
│     └─── Memoizes event handler                         │
│                                                          │
│  2. Cleanup in useEffect                                │
│     ├─── Removes event listener on unmount             │
│     └─── Prevents memory leaks                          │
│                                                          │
│  3. Early returns in handler                            │
│     ├─── Exits fast if typing in input                 │
│     └─── Minimal processing when not needed             │
│                                                          │
│  4. State checks before actions                         │
│     ├─── if (!isRefreshing) before refresh             │
│     └─── Prevents duplicate operations                  │
│                                                          │
│  5. Modal animations via CSS                            │
│     ├─── Hardware accelerated transforms               │
│     └─── Smooth 60fps animations                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Security Considerations

```
┌──────────────────────────────────────────────────────────┐
│              Security & Safety Features                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ✓ Input field detection                                │
│    - Prevents shortcuts from interfering with typing     │
│    - Respects user input contexts                       │
│                                                          │
│  ✓ Optional preventDefault                              │
│    - Allows browser defaults when needed                │
│    - Example: Esc key can still close browser dialogs   │
│                                                          │
│  ✓ State validation                                     │
│    - Checks refs exist before calling methods           │
│    - Prevents errors from undefined refs                │
│                                                          │
│  ✓ No eval() or dynamic code execution                 │
│    - All actions are pre-defined functions              │
│    - No security risks from user input                  │
│                                                          │
│  ✓ Proper event cleanup                                │
│    - No memory leaks                                    │
│    - No orphaned event listeners                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## File Dependencies Graph

```
index.tsx
    │
    └─── App.tsx
            │
            ├─── hooks/useKeyboardShortcuts.ts
            │         (no dependencies)
            │
            ├─── components/RegionSearch.tsx
            │         ├─── React (forwardRef, useImperativeHandle)
            │         └─── types.ts
            │
            └─── components/ShortcutsHelpModal.tsx
                      ├─── React (useEffect)
                      └─── index.css (for animations)

index.html
    │
    └─── index.css
            └─── Tailwind CSS
            └─── Custom animations
```

## Browser Compatibility Matrix

```
┌─────────────────────────────────────────────────────────────┐
│          Feature Support Across Browsers                    │
├──────────────┬────────┬─────────┬─────────┬────────────────┤
│   Feature    │ Chrome │ Firefox │ Safari  │   Edge         │
├──────────────┼────────┼─────────┼─────────┼────────────────┤
│ keydown evt  │   ✅   │   ✅    │   ✅    │     ✅         │
│ forwardRef   │   ✅   │   ✅    │   ✅    │     ✅         │
│ useCallback  │   ✅   │   ✅    │   ✅    │     ✅         │
│ CSS anims    │   ✅   │   ✅    │   ✅    │     ✅         │
│ Portal       │   ✅   │   ✅    │   ✅    │     ✅         │
└──────────────┴────────┴─────────┴─────────┴────────────────┘

All features: ✅ Full Support
Minimum versions:
  - Chrome: 70+
  - Firefox: 65+
  - Safari: 12+
  - Edge: 79+ (Chromium)
```

---

**Architecture Status**: ✅ Production Ready
**Last Updated**: 2025-11-19
