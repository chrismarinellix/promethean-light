# Pod Structure Presentation Editor Skill

## Trigger
Use this skill when user says: "update presentation", "edit pod structure", "change teams", "modify org chart", or references the pod-structure-analysis presentation.

## Target File
`C:\Code\projects\pod-structure-analysis\presentation-DRAFT-senior-review.html`

## Quick Reference - Team Structure

### Australian Teams (AU-1 to AU-4)
Located in the "Project Teams" section with grid layout.

**Current Structure:**
- **AU-1: Ajith** - Ajith Tennakoon (lead), Owais Raja, Syafiq Ishamuddin, Hayden Brunjes | Projects: Armidale, Haughton, Gerogery
- **AU-2: Ed** - Eduardo Laygo (lead), Komal Gaikwad, Khadija Kobra | Projects: Sandy SF, Sandy Hybrid, Wellington, Upper Calliope
- **AU-3: Momtazur** - Momtazur Rahman (lead), Shahrul Nizam, Amani | Projects: Markaranka BESS
- **AU-4: Zabir** - Zabir (lead), Dominic Moncada | Projects: TBD

### International Teams (IN-1, MY-1)
Located in the dashed orange "INTERNATIONAL" box.

- **IN-1: Faraz** (purple border) - Faraz Khan (lead), Chandan Singh, Abhinit Gaurav | India
- **MY-1: Amani S** (cyan border) - Amani Syafiqah (Malaysia Region Lead) | Malaysia

## Common Operations

### Add Person to Team
Find the team's `<div>` block and add a new `<p>` tag:
```jsx
<p>New Person Name</p>
```

### Remove Person from Team
Delete the corresponding `<p>` tag for that person.

### Add Project to Team
Find the team's projects section (after `borderTop: '1px dashed'`) and add:
```jsx
<p>New Project Name</p>
```

### Change Team Lead
Update the person with `fontWeight: 'bold'` and the diamond symbol `◆`

### Add New Team Box
Copy an existing pod-card div and modify:
- Team header (AU-X or IN-X/MY-X)
- Lead name with `◆` symbol
- Team members
- Projects list

## Styling Reference

### Team Card Colors
- **Standard AU teams**: Green tint (`rgba(0,227,169,...)`)
- **India teams (purple)**: `rgba(139, 92, 246, ...)`, text color `#a78bfa`
- **Malaysia teams (cyan)**: `rgba(6, 182, 212, ...)`, text color `#67e8f9`
- **Leadership (gold)**: `rgba(255,215,0, ...)`, text color `#ffd700`

### Special Styling
- **Lead indicator**: `◆` symbol after name
- **Projects section**: Dashed border top, green text `#86efac`
- **International box**: Dashed orange border `rgba(255,165,0,0.4)`

## Interpretation Guide

When user says:
- "add X to Y's team" → Add person X to team Y's member list
- "remove X" → Delete the `<p>` tag containing X
- "put X under Y" → Add X to Y's team members
- "give X project Z" → Add project Z to X's team projects
- "circle X" → Add dashed border styling around X
- "move X to the right" → Reposition in flex layout or create new column

## After Each Change
Always run:
```bash
start "" "C:\Code\projects\pod-structure-analysis\presentation-DRAFT-senior-review.html"
```
To refresh the browser and show the user the changes.

## Search Patterns

To find specific content in the file:
- Teams section: Search for `{/* Project Teams */}`
- International section: Search for `{/* International Teams */}`
- Specific person: Search for their name
- Projects list: Search for `color: '#86efac'` (project text color)
