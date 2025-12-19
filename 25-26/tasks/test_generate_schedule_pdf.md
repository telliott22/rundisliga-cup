# Test Task: Generate Schedule PDF

## Purpose
1. Test that the scheduler is working correctly
2. Generate a PDF of the full cup schedule to share

## Task
Generate a PDF document containing:
- Full fixture list (all 10 rounds)
- Cup schedule with dates
- Knockout bracket structure
- Rules summary

## Steps

### 1. Confirm scheduler is working
If you're seeing this, the scheduler notification worked! 🎉

### 2. Generate the Schedule PDF
Create a PDF with the full cup schedule. Options:

**Option A: Use Python with reportlab/fpdf**
```bash
pip3 install fpdf2
python3 scripts/generate_schedule_pdf.py
```

**Option B: Convert markdown to PDF**
```bash
# Install pandoc if needed
brew install pandoc
pandoc fixtures.md -o fixtures.pdf
```

**Option C: Create HTML and print to PDF**
Generate a styled HTML file and save as PDF.

### 3. Save the PDF
Save to `images/rundisliga_cup_schedule.pdf`

### 4. Let Tim know
The PDF is ready to share with the WhatsApp group!

## Content to Include

```
RUNDISLIGA CUP 25/26
====================

FULL SCHEDULE
-------------
GROUP STAGE
Round 1 - GW21 (Jan 6, 2026)
Round 2 - GW22 (Jan 17)
... etc

FIXTURES
--------
Round 1 fixtures...
Round 2 fixtures...
... etc

RULES
-----
- Win = 3 points
- Draw = 1 point
- Loss = 0 points
- Top 8 qualify for knockouts
```
