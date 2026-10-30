---
name: AgriShield AI
colors:
  surface: '#f7faf3'
  surface-dim: '#d7dbd4'
  surface-bright: '#f7faf3'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f5ed'
  surface-container: '#ebefe8'
  surface-container-high: '#e6e9e2'
  surface-container-highest: '#e0e4dc'
  on-surface: '#181d18'
  on-surface-variant: '#404940'
  inverse-surface: '#2d322d'
  inverse-on-surface: '#eef2eb'
  outline: '#707a6f'
  outline-variant: '#bfc9bd'
  surface-tint: '#1f6c3a'
  primary: '#004c22'
  on-primary: '#ffffff'
  primary-container: '#166534'
  on-primary-container: '#93e0a2'
  inverse-primary: '#8bd79b'
  secondary: '#006e2b'
  on-secondary: '#ffffff'
  secondary-container: '#6cff8a'
  on-secondary-container: '#00742e'
  tertiary: '#004c23'
  on-tertiary: '#ffffff'
  tertiary-container: '#006632'
  on-tertiary-container: '#56e989'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a6f4b5'
  primary-fixed-dim: '#8bd79b'
  on-primary-fixed: '#00210b'
  on-primary-fixed-variant: '#005226'
  secondary-fixed: '#6cff8a'
  secondary-fixed-dim: '#4ce171'
  on-secondary-fixed: '#002108'
  on-secondary-fixed-variant: '#00531f'
  tertiary-fixed: '#6dfe9c'
  tertiary-fixed-dim: '#4de082'
  on-tertiary-fixed: '#00210c'
  on-tertiary-fixed-variant: '#005227'
  background: '#f7faf3'
  on-background: '#181d18'
  surface-variant: '#e0e4dc'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 24px
  margin: 32px
  space-xs: 4px
  space-sm: 8px
  space-md: 16px
  space-lg: 24px
  space-xl: 48px
---

## Brand & Style

AgriShield AI is built for enterprise agricultural technology, balancing heavy analytical rigor with accessibility for field operations. The design system leverages a **Minimalism** framework paired with high-contrast functionalism to ensure usability under direct sunlight in rural environments and during high-stakes enterprise monitoring sessions. 

The emotional response should be one of absolute reliability, precision, and ecological stewardship. The UI avoids unnecessary decoration in favor of structural clarity, letting dense geospatial, meteorological, and yield-prediction data breathe through generous whitespace and meticulous typographic hierarchy.

## Colors

The palette is rooted in functional agrarian tones, prioritizing high legibility and natural harmony. 

- **Primary (`#166534`)**: Deep forest green used for primary actions, heavy structural framing, and high-emphasis data points.
- **Secondary (`#16BE53`)**: Vibrant mid-tier green used for active states, secondary buttons, and navigational highlights.
- **Accent (`#09B960`)**: Vivid sprout green reserved strictly for positive indicators, yield surpluses, and system-nominal badges.
- **Background (`#F8FAF7`) & Surface (`#FFFFFF`)**: Crisp, dew-kissed off-white foundations that reduce eye fatigue during extended monitoring shifts.
- **Text (`#17251C` / `#647067`)**: Deep charcoal-green for primary legibility paired with muted sage-gray for metadata.
- **Feedback (`#F59E0B` / `#DC2626`)**: High-visibility amber for environmental warnings and saturated crimson for critical crop stress or hardware failure.

## Typography

Typography pairs the welcoming, modern geometric character of **Plus Jakarta Sans** for headlines with the utilitarian precision of **Inter** for dense data tables and body copy. 

- For viewports below 768px, scale down `headline-xl` to 28px and `headline-lg` to 24px to prevent aggressive wrapping on mobile field devices.
- Maintain strict adherence to defined line heights to ensure tabular crop yields and sensor readouts remain scannable.

## Layout & Spacing

This design system utilizes a **12-column fluid grid system** anchored by a max-width enterprise container (1440px) for desktop dashboards, collapsing intelligently into a single-column layout for mobile field operations.

- **Gutters & Margins:** Maintain a consistent 24px gutter between dashboard panels and 32px outer canvas margins on desktop, scaling down to 16px on mobile devices to maximize usable viewport width for maps and charts.
- **Rhythm:** All component padding and spatial relationships must strictly adhere to the defined `space-*` token scale to ensure predictable vertical rhythm across dense analytics panels.

## Elevation & Depth

Visual hierarchy relies on **low-contrast outlines** and structured tonal layering rather than heavy drop shadows. 

- Use subtle borders (`#E5EAE5`) to section analytical panels, map viewports, and telemetry cards.
- Elevate active modal dialogs and floating map controls using hyper-diffused, low-opacity shadows tinted with the primary green hue (`rgba(22, 101, 52, 0.08)`) to maintain a grounded, organic aesthetic.

## Shapes

The shape language uses a **Rounded** approach (`roundedness: 2`), balancing industrial efficiency with friendly approachability. 

- Base components (inputs, buttons, standard cards) feature a comfortable `0.5rem` (8px) border radius.
- Major structural containers and data visualization wrappers utilize `1rem` to `1.5rem` radii to soften dense informational clusters without sacrificing the systematic enterprise feel.

## Components

- **Buttons:** Primary buttons use the deep forest green (`#166534`) background with high-contrast white text, an 8px border radius, and a subtle scale-up or darkening state on hover. Secondary actions use outlined variants with neutral borders and primary-colored text.
- **Chips & Badges:** Compact indicators used for crop health statuses (e.g., "Optimal", "Stressed") featuring soft tinted backgrounds matching accent, warning, or critical tokens.
- **Lists:** Clean, divider-separated data rows optimized for sensor logs and telemetry feeds, featuring alternating row backgrounds for scannability.
- **Checkboxes & Radio Buttons:** High-contrast square and circular inputs with clear active fill states in primary green, designed for touch-target reliability in field conditions.
- **Input Fields:** Outlined text boxes with 8px radii, clear internal label positioning, and explicit error states utilizing the critical red token.
- **Cards:** Structured container cards featuring flat white surfaces, subtle 1px borders (`#E5EAE5`), and internal padding scaling with `space-lg`. Ideal for encapsulating single-field telemetry or weather forecasts.
- **Data Visualizations:** Specialized dashboard widgets featuring muted grid lines, primary green trend lines, and distinct amber/crimson threshold markers for immediate anomaly detection.