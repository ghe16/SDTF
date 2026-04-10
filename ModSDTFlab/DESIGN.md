# DESIGN.md - SDTFLab Design System

## 1. Vision: "The Observational Engine"
The design treats the UI as a living window into a high-velocity distributed network. It balances academic data rigor with high-end aerospace interface sophistication.

## 2. Core Color Palette (Dark Mode)
| Role | Color | Hex |
| :--- | :--- | :--- |
| **Base Surface** | Background | `#0B1326` |
| **Surface Low** | Primary Sections | `#131B2E` |
| **Surface Standard** | Interactive Units | `#171F33` |
| **Surface High** | Elevated Details | `#222A3D` |
| **Primary** | Highlights/Action | `#89CEFF` |
| **Secondary** | Success/Active | `#4EDEA3` |
| **Tertiary** | Leader/Alert | `#FFB95F` |
| **Error** | Critical State | `#FFB4AB` |

### Surface Philosophy
- **No-Line Rule**: Avoid 1px solid borders; use background shifts or "Ghost Borders" (15% opacity `outline_variant`).
- **Glassmorphism**: 70% opacity fill with 12px backdrop blur for primary cards.

## 3. Typography
- **Interface & Headlines**: **Inter**
  - Display metrics use large scales with tight tracking (-0.02em).
- **Technical Data**: **JetBrains Mono**
  - Used for logs, node IDs, IP addresses, and throughput.
- **Tonality**: Primary text: `#DAE2FD` | Secondary labels: `#BEC8D2`.

## 4. Spacing & Elevation
- **Spacing Scale**: Base 1 (increments follow a standard technical grid).
- **Layering Principle**: `surface_container_lowest` (#060E20) for inset areas (logs); `surface_container_highest` (#2D3449) for popovers.
- **Shadows**: Extra-diffused shadows for modals: `0 20px 40px rgba(6, 14, 32, 0.5)`.

## 5. Key Components
### Buttons
- **Primary**: Solid `#89CEFF` background, 4px corner radius.
- **Ghost**: Outline at 20% opacity, primary color text.

### Status Chips
- **Active Node**: Secondary text on 10% secondary fill.
- **Leader Node**: Tertiary text on 10% tertiary fill.

### Monitoring Elements
- **Log Matrix**: `surface_container_lowest` background, JetBrains Mono font, zebra-striping (2% opacity highlight every 3rd line).
- **Synchronized Timelines**: 1px `primary` playhead (50% opacity) spanning multiple graphs.

### Cards
- **Construction**: No internal dividers. Use spacing (24px padding) and tonal shifts to separate sections.

## 6. Screens Overview
- **SDTF Lab Home**: Bento-style algorithm selection and high-level health metrics.
- **Algorithm Dashboard**: Deep-dive execution lab with topology graphs, log streams, and control panels.
