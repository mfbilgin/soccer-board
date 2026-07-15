---
name: GoalMaster
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c4c9ac'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#8e9379'
  outline-variant: '#444933'
  surface-tint: '#abd600'
  primary: '#ffffff'
  on-primary: '#283500'
  primary-container: '#c3f400'
  on-primary-container: '#556d00'
  inverse-primary: '#506600'
  secondary: '#b3c5ff'
  on-secondary: '#002b75'
  secondary-container: '#0266ff'
  on-secondary-container: '#f9f7ff'
  tertiary: '#ffffff'
  on-tertiary: '#690003'
  tertiary-container: '#ffdad5'
  on-tertiary-container: '#ca0a0f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#c3f400'
  primary-fixed-dim: '#abd600'
  on-primary-fixed: '#161e00'
  on-primary-fixed-variant: '#3c4d00'
  secondary-fixed: '#dae1ff'
  secondary-fixed-dim: '#b3c5ff'
  on-secondary-fixed: '#001849'
  on-secondary-fixed-variant: '#003fa4'
  tertiary-fixed: '#ffdad5'
  tertiary-fixed-dim: '#ffb4aa'
  on-tertiary-fixed: '#410001'
  on-tertiary-fixed-variant: '#930005'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Anybody
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 52px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Anybody
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Anybody
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Anybody
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 30px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 32px
  xl: 48px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style
The design system is engineered for a high-stakes, competitive football prediction environment. The brand personality is **energetic, authoritative, and precision-driven**, capturing the adrenaline of live match days. It targets a digitally-native sports audience that values speed and clarity.

The visual style is a fusion of **Modern Dark Mode** and **Glassmorphism**, utilizing deep atmospheric backgrounds to let vibrant neon accents "pop." We employ subtle glows and translucent overlays to create a sense of depth and premium quality, reminiscent of high-end sports broadcast graphics.

## Colors
The palette is dominated by **Pitch Black (#0F172A)** and **Deep Stadium Navy (#1E293B)** to ensure maximum contrast for the action colors.

- **Primary (Neon Green):** Reserved for the most critical actions, confirmation states, and winning predictions. It represents energy and "go" signals.
- **Secondary (Electric Blue):** Used for navigation, secondary interactive elements, and informative data visualizations.
- **Tertiary (Signal Red):** Dedicated to live match indicators, errors, or high-urgency alerts.
- **Glass/Surface:** Surfaces use semi-transparent variants of the neutral shades with a background blur (16px–24px) to maintain legibility over dynamic backgrounds.

## Typography
The typography strategy balances raw power with technical precision. 

**Anybody** is used for headlines; its variable width and bold weights evoke the movement and impact of sports branding. We use uppercase styling for top-level headers to increase the "stadium announcement" feel. 

**Hanken Grotesk** provides a clean, modern sans-serif experience for player names, match details, and descriptions, ensuring high readability during fast-paced scrolling. 

**JetBrains Mono** is utilized for technical data, such as betting odds, scores, and timers, providing a "data-driven" look that implies accuracy.

## Layout & Spacing
The layout follows a **Fluid Grid** model designed primarily for mobile-first interactions. We use a 4-column grid for mobile and a 12-column grid for tablet/desktop.

The spacing rhythm is based on a **4px baseline**, creating tight, purposeful groupings of data. Content cards (like Match Cards) should use `md (24px)` padding to feel airy despite the dark theme. Gutters are kept at `sm (16px)` to maximize the real estate for match statistics and prediction sliders.

## Elevation & Depth
Depth is created through **Glassmorphism** and **Tonal Layering** rather than traditional heavy shadows.

- **Level 0 (Background):** Deepest Navy (#0F172A).
- **Level 1 (Cards/Lists):** Surface Navy (#1E293B) with a 1px inner border of 10% white to define edges.
- **Level 2 (Modals/Popovers):** Glass layer with 60% opacity and 20px backdrop blur. 
- **Active State Glow:** Interactive elements like the "Predict" button emit a soft Neon Green outer glow (`box-shadow: 0 0 15px rgba(204, 255, 0, 0.4)`) to simulate a light source in a dark stadium.

## Shapes
The shape language is **Rounded (0.5rem)**, striking a balance between modern tech and approachable gaming. 

- **Small elements (Chips, Tags):** Use `rounded-lg` (1rem) to create a soft, pill-like feel.
- **Large elements (Match Cards, Modals):** Use `rounded-xl` (1.5rem) to soften the screen's layout.
- **Interactive inputs:** Use standard `rounded` (0.5rem) for a crisp, functional appearance.

## Components

### Buttons
- **Primary:** Neon Green background, Black text (Anybody Bold). No shadow, but a soft glow on hover/active states.
- **Secondary:** Electric Blue outline (2px) with transparent background and Blue text.
- **Ghost:** Transparent background with white text, used for less urgent navigation.

### Cards (Match/Player)
Match cards are the core component. They feature a 1px subtle border, a slight gradient from top-left (#2D3748) to bottom-right (#1E293B), and utilize Glassmorphism for the "Live" score overlays.

### Inputs
Input fields use a high-contrast design: Pitch Black background with a 1px stroke that turns Electric Blue when focused. Labels use JetBrains Mono for a "utility" aesthetic.

### Chips & Badges
Used for match status (e.g., "LIVE", "FINISHED") and categories. Live badges must pulse with a Tertiary Red glow.

### Prediction Sliders
A custom component for GoalMaster. The track is Deep Navy, while the thumb is a Neon Green "glow" orb that leaves a trail of green as it slides, indicating the user's confidence level.

### Rewards/Success States
Full-screen glass overlays with "confetti" particles in Neon Green and Electric Blue. Typography scales up to `display-lg` for win announcements.