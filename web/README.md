# BlackRoad Websites

Beautiful retro-futuristic websites with Matrix vibes and Y2K aesthetics.

## 🌐 Live Sites

All websites are built with the unified BlackRoad design system featuring:
- Spectrum gradient colors (gold → orange → pink → purple → indigo → blue → cyan → green)
- Retro CRT effects with scanlines
- Interactive animations and sound effects
- Matrix/Y2K aesthetic
- No "slave" terminology - ethical AI language throughout

### Websites

1. **index.html** - Navigation hub for all BlackRoad sites
2. **blackroad.io.html** - Quantum AI platform landing page
3. **blackroadinc.us.html** - Corporate website
4. **blackroad-showcase.html** - Design system showcase
5. **blackroad-pi-boot.html** - Pi boot screen with CRT effects
6. **blackroad-social.html** - Social platform demo
7. **quantum.html** - Quantum computing demo

## 🚀 Quick Start

### Local Development

```bash
# Option 1: Using the serve script (recommended)
cd web
chmod +x serve.sh
./serve.sh

# Option 2: Using Python directly
cd web
python3 -m http.server 8080

# Option 3: Using npm
cd web
npm run serve
```

Then open http://localhost:8080 in your browser!

### URLs

When running locally:
- Navigation: http://localhost:8080/
- Platform: http://localhost:8080/blackroad.io.html
- Corporate: http://localhost:8080/blackroadinc.us.html
- Design System: http://localhost:8080/blackroad-showcase.html
- Pi Boot: http://localhost:8080/blackroad-pi-boot.html
- Social: http://localhost:8080/blackroad-social.html
- Quantum: http://localhost:8080/quantum.html

## 🎨 Design System

All sites use:
- **CSS**: `assets/blackroad.css` - Complete design system
- **JS**: `assets/blackroad.js` - Interactive utilities and effects

### Key Features
- CRT screen effects with scanlines
- Terminal text with glow
- Animated gradients
- Sound effects (beeps, clicks, power-up)
- Toast notifications
- Loading indicators
- Particle effects
- Matrix backgrounds

## 📦 Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd web
vercel

# Production deployment
vercel --prod
```

### Deploy to Netlify

1. Connect your GitHub repo
2. Set build settings:
   - Build command: (leave empty)
   - Publish directory: `web`
3. Deploy!

### Deploy to GitHub Pages

```bash
# Push to gh-pages branch
git subtree push --prefix web origin gh-pages
```

## 🎮 Interactive Features

- **Sound Effects**: Retro beeps and clicks on interactions
- **Animations**: Smooth fade-ins, slides, pulses, glows
- **Terminal Demo**: Auto-running command sequences
- **Particle Bursts**: On button clicks and special events
- **Konami Code**: Try ↑↑↓↓←→←→BA on index.html!
- **Smooth Scrolling**: All anchor links animate smoothly

## 📱 Responsive

All sites are fully responsive and work on:
- Desktop (1920px+)
- Laptop (1400px)
- Tablet (768px)
- Mobile (480px)

## 🛠️ Technology Stack

- **HTML5**: Semantic markup
- **CSS3**: Custom properties, Grid, Flexbox, Animations
- **JavaScript**: Vanilla ES6+, No frameworks needed
- **Python**: Built-in HTTP server for local dev
- **Vercel**: Production deployment platform

## 🎯 Performance

- Minimal dependencies (just BlackRoad CSS/JS)
- Optimized animations
- Lazy loading
- Compressed assets
- Fast load times (<1s)

## ✨ Special Thanks

Built with love by the BlackRoad team.

**SPECTRUM INITIALIZED** 🌈

---

© 2025 BlackRoad Technologies, Inc.
