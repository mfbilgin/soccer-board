import { StyleSheet } from 'react-native';

export const COLORS = {
  background: 'transparent', // Will be overlaid by ImageBackground
  darkBase: '#1a4a15',       // Deeper Green for fallback
  surface: '#25671e',    // Dark Forest Green (from palette) for cards
  surfaceHighlight: 'rgba(255, 255, 255, 0.15)',
  surfaceVariant: '#318228',
  
  primary: '#48a111',    // Bright Grass Green (from palette)
  primaryDim: '#3a800d',
  
  secondary: '#f2b50b',  // Golden Yellow (from palette) for coins/gems/highlights
  danger: '#ca0a0f',     // Tertiary Red (Live/Alert)
  
  text: '#ffffff',       // White text for contrast on dark green cards
  textMuted: '#e0e0e0',  
  textDark: '#0b1326',   // For text on primary buttons
  
  outline: '#8e9379',
};

export const SIZES = {
  base: 4,
  xs: 8,
  sm: 16,
  md: 24,
  lg: 32,
  xl: 48,
  
  fontSm: 12,
  font: 14,
  fontMd: 16,
  fontLg: 18,
  titleSm: 24,
  title: 32,
  titleLg: 48,
  
  radiusSm: 4,
  radius: 8,
  radiusMd: 12,
  radiusLg: 16,
  radiusXl: 24,
};

export const FONTS = {
  heading: 'Outfit_700Bold',
  headingBlack: 'Outfit_900Black',
  body: 'Inter_400Regular',
  bodyBold: 'Inter_700Bold',
  mono: 'JetBrainsMono_500Medium',
};

export const GLOBAL_STYLES = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  glassContainer: {
    backgroundColor: COLORS.surface,
    borderRadius: SIZES.radiusLg,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    overflow: 'hidden',
  },
  primaryButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: SIZES.sm,
    paddingHorizontal: SIZES.md,
    borderRadius: SIZES.radius,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.4,
    shadowRadius: 15,
    elevation: 5,
  },
  primaryButtonText: {
    color: COLORS.textDark,
    fontSize: SIZES.fontLg,
    fontFamily: FONTS.heading,
    textTransform: 'uppercase',
  },
});
