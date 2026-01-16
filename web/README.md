# PNP Web Interface

Modern web interface for the P vs NP Lock Experimentation tool, designed for GitHub Pages deployment.

## Files

- **index.html** - Landing page with project overview and navigation
- **styles.css** - Modern dark theme CSS with responsive design
- **manual.html** - Interactive lock builder with visual feedback

## Features

### Landing Page (index.html)
- Project introduction and explanation
- Interactive navigation to tools
- Features overview
- GitHub repository link
- Responsive design for mobile/desktop

### Manual Lock Builder (manual.html)
- **Left Panel (Controls):**
  - Initialize lock with number of dials
  - Add negation links (Not constraints)
  - Add OR clauses
  - View all constraints with remove option
  - Download lock as JSON file

- **Right Panel (Visualization):**
  - Canvas-based interactive diagram
  - Dials shown as numbered circles
  - Negation links shown as red lines
  - OR clauses shown as green triangles
  - Legend explaining visual elements

### Features:
✅ Real-time validation
✅ Visual feedback for all operations
✅ Prevent duplicate constraints
✅ Download in correct JSON format
✅ Responsive layout
✅ Dark theme with good contrast

## Design

**Color Scheme:**
- Primary background: `#0d1117`
- Card background: `#21262d`
- Accent blue: `#58a6ff` (dials, primary buttons)
- Accent red: `#f85149` (negation links)
- Accent green: `#3fb950` (OR clauses)

**Typography:**
- Sans-serif: System fonts for readability
- Monospace: For code and technical elements

**Layout:**
- CSS Grid and Flexbox for responsive design
- Sticky sidebar on desktop
- Stacked layout on mobile

## Usage

### Local Testing
Open `index.html` in a web browser:
```bash
cd web/
python3 -m http.server 8000
# Visit http://localhost:8000
```

### GitHub Pages Deployment
1. Push to GitHub repository
2. Enable GitHub Pages in repository settings
3. Select branch (e.g., `main` or `gh-pages`)
4. Set source directory to `/web` (or root if moved)
5. Access at `https://l-87hjl.github.io/PNP/`

## Browser Compatibility

Tested on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

Requires:
- Canvas API support
- ES6 JavaScript support
- CSS Grid and Flexbox support

## Future Enhancements

Planned features:
- [ ] Automatic instance generator page
- [ ] SAT solver interface (upload instance, get solution)
- [ ] Solution visualizer
- [ ] Example instances gallery
- [ ] Step-by-step solving animation
- [ ] Export as PNG/SVG
- [ ] Dark/light theme toggle

## File Structure

```
web/
├── index.html          # Landing page
├── manual.html         # Lock builder tool
├── styles.css          # Shared styles
└── README.md          # This file
```

## JavaScript Architecture (manual.html)

**Global State:**
```javascript
lockState = {
    numDials: 0,
    binaryPins: [],
    negations: [],
    clauses: []
}
```

**Key Functions:**
- `createLock()` - Initialize lock with dials
- `addNegation()` - Add negation constraint
- `addClause()` - Add OR clause constraint
- `visualizeLock()` - Render canvas visualization
- `downloadJSON()` - Export as JSON file

**Validation:**
- Dial range checking
- Duplicate constraint detection
- Distinct dial validation
- Input sanitization

## Contributing

To add new pages:
1. Create HTML file in `web/`
2. Link `styles.css` for consistent styling
3. Add navigation link from `index.html`
4. Update this README
5. Test responsiveness

## License

Same as parent project (MIT License)
