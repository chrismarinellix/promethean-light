# Weekly Client Checklist System

A standardized system for conducting weekly client check-ins on grid connection study projects.

## 📁 Files in This Directory

### Core Templates

1. **weekly_client_checklist.html** ⭐
   - **Interactive HTML form** - Fill out in your browser
   - Has checkboxes, text fields, and auto-save functionality
   - Best for: Daily use during client calls
   - **How to use:**
     - Double-click to open in browser
     - Fill in during/after client call
     - Click "Save as HTML" to save completed version
     - Click "Print" for paper copy

2. **WEEKLY_CLIENT_CHECKLIST.md**
   - Markdown version of the checklist
   - Best for: Version control, plain text editing
   - Can be used with the Python email generator

3. **QUICK_REFERENCE_QUESTIONS.md**
   - **Print this!** One-page summary
   - 10 essential questions to ask
   - Red flag phrases to listen for
   - Best for: Keep at your desk during calls

### Documentation

4. **WEEKLY_CHECKLIST_GUIDE.md**
   - Complete user guide for the team
   - How to use the checklist
   - Email templates for client updates
   - Escalation criteria
   - Best practices

### Automation

5. **checklist_email_generator.py**
   - Python script to parse completed checklists
   - Auto-generates client emails
   - Auto-generates management summaries
   - **Usage:**
     ```bash
     # Single project
     python checklist_email_generator.py completed_checklist.md

     # All projects in a folder
     python checklist_email_generator.py --all-projects ./weekly_checklists/
     ```

## 🚀 Quick Start

### For Engineers (First Time)

1. **Print the quick reference:**
   - Open `QUICK_REFERENCE_QUESTIONS.md`
   - Print it or keep it on second monitor

2. **Use the HTML form:**
   - Double-click `weekly_client_checklist.html`
   - Bookmark it in your browser
   - Fill it out during your next client call

3. **Save your completed checklist:**
   - Click "Save as HTML" button
   - Name it: `ProjectName_2025-11-21_checklist.html`
   - Store in a `completed_checklists` folder

### For Team Leaders (Rollout)

1. **Review the guide:**
   - Read `WEEKLY_CHECKLIST_GUIDE.md`
   - Customize if needed for your team

2. **Team training (15 mins):**
   - Show the HTML form
   - Demonstrate filling it during a mock call
   - Explain the "why" - catching scope changes early

3. **First week pilot:**
   - Each engineer completes ONE checklist
   - Review together in next team meeting
   - Adjust questions if needed

## 📋 Recommended Workflow

### Monday-Thursday (During Client Calls)
1. Open `weekly_client_checklist.html` in browser
2. Keep `QUICK_REFERENCE_QUESTIONS.md` visible
3. Check boxes as conversation flows naturally
4. Add notes in text fields
5. Save completed form when done

### Friday (Weekly Summary)
1. Review all your completed checklists for the week
2. Use Section 10 summaries to draft client emails
3. Run email generator for management summary:
   ```bash
   python checklist_email_generator.py --all-projects ./my_completed_checklists/
   ```

## 🎯 Key Benefits

- ✅ Catches scope changes when first mentioned
- ✅ Early warning system for client dissatisfaction
- ✅ Consistent communication across all projects
- ✅ Management visibility into project health
- ✅ CYA documentation with timestamps
- ✅ Professional image with clients

## 📊 File Organization

Recommended folder structure:

```
C:\Code\Promethian Light\
├── checklists\                          ← You are here
│   ├── weekly_client_checklist.html    ← Daily use
│   ├── QUICK_REFERENCE_QUESTIONS.md    ← Print this
│   ├── WEEKLY_CHECKLIST_GUIDE.md       ← Read this
│   └── checklist_email_generator.py    ← Automation
│
└── completed_checklists\                ← Create this folder
    ├── 2025-11\
    │   ├── ProjectA_2025-11-21_checklist.html
    │   ├── ProjectB_2025-11-21_checklist.html
    │   └── ...
    └── 2025-12\
        └── ...
```

## 💡 Pro Tips

1. **Don't skip weeks** - Even "nothing changed" is valuable data
2. **Be honest about health ratings** - Yellow/Red gets you support
3. **Complete same day** - Memory fades fast
4. **Focus on Sections 2 & 4** - Scope changes and satisfaction are critical
5. **Print the quick reference** - Seriously, print it

## 🚨 Escalate Immediately If:

- 🔴 Client expresses serious dissatisfaction
- 🔴 Scope change worth >$10k mentioned
- 🔴 Client requesting significant out-of-scope work
- 🔴 Deadline that definitely cannot be met
- 🔴 Project goes from Green to Red in one week

## 🔧 Customization

Feel free to customize:
- Add project-specific questions (solar/wind/BESS specific)
- Remove sections not relevant to your work
- Adjust health rating thresholds
- Modify email templates

Just maintain the core:
- Scope change tracking (Section 2)
- Client satisfaction (Section 4)
- Overall health (Section 10)

## 📞 Support

Questions? Ask:
- Your PM for process guidance
- Senior engineers for examples
- Team lead for customization

## 📝 Version

- **Created:** 2025-11-21
- **Version:** 1.0
- **Maintained by:** Engineering Team

---

**Remember:** 5-10 minutes weekly prevents hours of problems later.
