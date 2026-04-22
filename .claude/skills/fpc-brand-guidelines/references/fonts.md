# FPC Griffin — Font Reference

All font files live in `assets/fonts/`. Install or load them before rendering any artifact.

---

## How to Install Fonts (Python / bash)

```bash
# Install system-wide (Linux)
cp assets/fonts/clarendon-urw/*.otf /usr/local/share/fonts/
cp assets/fonts/cmg-sans/*.ttf /usr/local/share/fonts/
fc-cache -fv

# Verify
fc-list | grep -i clarendon
fc-list | grep -i "CMG"
```

## How to Use in HTML/CSS Artifacts

```css
@font-face {
  font-family: 'Clarendon URW';
  src: url('assets/fonts/clarendon-urw/clarendonurwextwid-med.otf') format('opentype');
  font-weight: 500;
  font-style: normal;
}
@font-face {
  font-family: 'Clarendon URW';
  src: url('assets/fonts/clarendon-urw/clarendonurwextwid-medobl.otf') format('opentype');
  font-weight: 500;
  font-style: italic;
}
@font-face {
  font-family: 'CMG Sans';
  src: url('assets/fonts/cmg-sans/CMGSans-Regular.ttf') format('truetype');
  font-weight: 400;
  font-style: normal;
}
/* Add more @font-face blocks as needed for each weight/style used */
```

---

## Clarendon URW — 50 files

**Brand-preferred cut: Extended Wide (`clarendonurwextwid-*`)**
Use this cut for all display and heading text per the brand guide.

### Standard (`clarendonurw-*`)
| File | Weight | Style |
|------|--------|-------|
| clarendonurw-lig.otf | Light (300) | Normal |
| clarendonurw-ligobl.otf | Light (300) | Oblique |
| clarendonurw-reg.otf | Regular (400) | Normal |
| clarendonurw-regobl.otf | Regular (400) | Oblique |
| clarendonurw-med.otf | Medium (500) | Normal |
| clarendonurw-medobl.otf | Medium (500) | Oblique |
| clarendonurw-bol.otf | Bold (700) | Normal |
| clarendonurw-bolobl.otf | Bold (700) | Oblique |
| clarendonurw-extbol.otf | ExtraBold (800) | Normal |
| clarendonurw-extbolobl.otf | ExtraBold (800) | Oblique |

### Narrow (`clarendonurwnar-*`)
| File | Weight | Style |
|------|--------|-------|
| clarendonurwnar-lig.otf | Light | Normal |
| clarendonurwnar-ligobl.otf | Light | Oblique |
| clarendonurwnar-reg.otf | Regular | Normal |
| clarendonurwnar-regobl.otf | Regular | Oblique |
| clarendonurwnar-med.otf | Medium | Normal |
| clarendonurwnar-medobl.otf | Medium | Oblique |
| clarendonurwnar-bol.otf | Bold | Normal |
| clarendonurwnar-bolobl.otf | Bold | Oblique |
| clarendonurwnar-extbol.otf | ExtraBold | Normal |
| clarendonurwnar-extbolobl.otf | ExtraBold | Oblique |

### Wide (`clarendonurwwid-*`)
| File | Weight | Style |
|------|--------|-------|
| clarendonurwwid-lig.otf | Light | Normal |
| clarendonurwwid-ligobl.otf | Light | Oblique |
| clarendonurwwid-reg.otf | Regular | Normal |
| clarendonurwwid-regobl.otf | Regular | Oblique |
| clarendonurwwid-med.otf | Medium | Normal |
| clarendonurwwid-medobl.otf | Medium | Oblique |
| clarendonurwwid-bol.otf | Bold | Normal |
| clarendonurwwid-bolobl.otf | Bold | Oblique |
| clarendonurwwid-extbol.otf | ExtraBold | Normal |
| clarendonurwwid-extbolobl.otf | ExtraBold | Oblique |

### Extended Narrow (`clarendonurwextnar-*`)
| File | Weight | Style |
|------|--------|-------|
| clarendonurwextnar-lig.otf | Light | Normal |
| clarendonurwextnar-ligobl.otf | Light | Oblique |
| clarendonurwextnar-reg.otf | Regular | Normal |
| clarendonurwextnar-regobl.otf | Regular | Oblique |
| clarendonurwextnar-med.otf | Medium | Normal |
| clarendonurwextnar-medobl.otf | Medium | Oblique |
| clarendonurwextnar-bol.otf | Bold | Normal |
| clarendonurwextnar-bolobl.otf | Bold | Oblique |
| clarendonurwextnar-extbol.otf | ExtraBold | Normal |
| clarendonurwextnar-extbolob.otf | ExtraBold | Oblique |

### Extended Wide (`clarendonurwextwid-*`) ★ BRAND PRIMARY
| File | Weight | Style |
|------|--------|-------|
| clarendonurwextwid-lig.otf | Light | Normal |
| clarendonurwextwid-ligobl.otf | Light | Oblique |
| clarendonurwextwid-reg.otf | Regular | Normal |
| clarendonurwextwid-regobl.otf | Regular | Oblique |
| clarendonurwextwid-med.otf | **Medium (500)** | Normal ← primary heading weight |
| clarendonurwextwid-medobl.otf | Medium (500) | Oblique |
| clarendonurwextwid-bol.otf | Bold (700) | Normal |
| clarendonurwextwid-bolobl.otf | Bold (700) | Oblique |
| clarendonurwextwid-extbol.otf | ExtraBold (800) | Normal |
| clarendonurwextwid-extbolob.otf | ExtraBold (800) | Oblique |

---

## CMG Sans — 32 files

**Brand-preferred weights: Regular (400), Medium (500), SemiBold (600), Bold (700)**

### Standard
| File | Weight | Style |
|------|--------|-------|
| CMGSans-Thin.ttf | Thin (100) | Normal |
| CMGSans-ThinItalic.ttf | Thin (100) | Italic |
| CMGSans-ExtraLight.ttf | ExtraLight (200) | Normal |
| CMGSans-ExtraLightItalic.ttf | ExtraLight (200) | Italic |
| CMGSans-Light.ttf | Light (300) | Normal |
| CMGSans-LightItalic.ttf | Light (300) | Italic |
| CMGSans-Regular.ttf | **Regular (400)** | Normal ← body text |
| CMGSans-Italic.ttf | Regular (400) | Italic |
| CMGSans-Medium.ttf | **Medium (500)** | Normal |
| CMGSans-MediumItalic.ttf | Medium (500) | Italic |
| CMGSans-MediumCAPS.ttf | Medium (500) | Small Caps |
| CMGSans-SemiBold.ttf | **SemiBold (600)** | Normal ← subhead/UI |
| CMGSans-SemiBoldItalic.ttf | SemiBold (600) | Italic |
| CMGSans-SemiBoldCAPS.ttf | SemiBold (600) | Small Caps |
| CMGSans-Bold.ttf | **Bold (700)** | Normal |
| CMGSans-BoldItalic.ttf | Bold (700) | Italic |
| CMGSans-BoldCAPS.ttf | Bold (700) | Small Caps |
| CMGSans-BoldSlab.ttf | Bold Slab | Normal |
| CMGSans-ExtraBold.ttf | ExtraBold (800) | Normal |
| CMGSans-ExtraBoldItalic.ttf | ExtraBold (800) | Italic |
| CMGSans-Black.ttf | Black (900) | Normal |
| CMGSans-BlackItalic.ttf | Black (900) | Italic |

### Condensed (`*Cn*`)
| File | Weight | Style |
|------|--------|-------|
| CMGSans-RegularCn.ttf | Regular | Normal |
| CMGSansCn-Italic.ttf | Regular | Italic |
| CMGSans-MediumCn.ttf | Medium | Normal |
| CMGSans-MediumCnCAPS.ttf | Medium | Small Caps |
| CMGSansMediumCn-Italic.ttf | Medium | Italic |
| CMGSans-SemiBoldCn.ttf | SemiBold | Normal |
| CMGSans-SemiBoldCn.ttf | SemiBold | Normal |
| CMGSansSemiBoldCn-Italic.ttf | SemiBold | Italic |
| CMGSans-BoldCn.ttf | Bold | Normal |
| CMGSans-BoldCnCAPS.ttf | Bold | Small Caps |
| CMGSansCn-BoldItalic.ttf | Bold | Italic |
