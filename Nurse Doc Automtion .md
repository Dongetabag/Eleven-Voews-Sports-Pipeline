# Skilled Nursing Narrative Converter

Automates the conversion of skilled nursing narratives from markdown format to professional, structured HTML reports.

## Features

✨ **Automatic Section Detection** - Intelligently parses and organizes content into:
- Patient Information (Demographics, Diagnosis, PMH)
- Visit Summary (Treatment Plan, Lab Monitoring)
- Assessment Findings (Physical, Wound, IV Site)
- Focus of Care (Objectives, Requirements)
- Homebound Status
- Patient Education
- Plan for Next Visit

🎨 **Professional Design** - Premium dark theme with:
- Custom typography (Playfair Display + Inter)
- Smooth animations and hover effects
- Responsive layout for all devices
- Print-friendly styling

📊 **Smart Parsing** - Automatically extracts:
- Patient demographics and medical history
- Treatment medications and schedules
- Assessment findings and vital signs
- Education topics and patient responses
- Dressing change dates and IV details

## Installation

No dependencies required! Uses Python 3.6+ standard library only.

```bash
# Make the script executable (optional)
chmod +x nursing_narrative_converter.py
```

## Usage

### Single File Conversion

```bash
# Basic usage - auto-generates output filename
python nursing_narrative_converter.py input.md

# Specify output filename
python nursing_narrative_converter.py input.md output.html

# Example
python nursing_narrative_converter.py Skilled_Nursing_Narrative.md Patient_Report.html
```

### Batch Processing

```bash
# Convert all markdown files in a directory
python batch_convert_narratives.py /path/to/markdown/files

# Specify output directory
python batch_convert_narratives.py /path/to/input /path/to/output
```

## Input Format

Your markdown files should follow this structure:

```markdown
**Skilled Nursing Narrative**  
**Patient: 71-year-old female**  
**Primary Diagnosis: Hardware complication wound infection; Nocardia infection**  
**Past Medical History: Anxiety, hyperlipidemia, depression, GERD**  
  
⸻  
  
**Visit Summary:**  
**Patient was seen today for skilled nursing assessment and IV antibiotic management...**  
  
⸻  
  
**Focus of Care:**  
**The primary focus of care is on infection management...**  
  
⸻  
  
**Homebound Status:**  
**Patient is considered homebound due to...**  
  
⸻  
  
**Education Provided:**  
**Patient was educated on:**  
**    •    Proper hand hygiene and infection prevention techniques.**  
**    •    Recognizing signs of IV complications...**  
```

### Section Dividers

Use any of these to separate sections:
- `⸻` (special character)
- `---` (three or more dashes)
- `***` (three or more asterisks)

## Output Structure

The converter generates HTML with these sections:

1. **Patient Information**
   - Demographics
   - Primary Diagnosis
   - Past Medical History (bulleted list)

2. **Visit Summary**
   - Current Treatment Plan
   - Laboratory Monitoring

3. **Assessment Findings**
   - Physical Assessment
   - Wound Assessment
   - IV Site Assessment

4. **Focus of Care**
   - Primary Objectives
   - Skilled Nursing Requirements

5. **Homebound Status**
   - Homebound Justification (with reasons)

6. **Patient Education**
   - Education Topics Covered
   - Patient Response

7. **Plan for Next Visit**
   - Scheduled Assessments

## Customization

### Modify Styling

Edit the CSS in the `generate_html()` method to customize:
- Colors and themes
- Typography
- Layout and spacing
- Responsive breakpoints

### Add New Sections

1. Create a parsing method: `_parse_new_section()`
2. Add to `parse_markdown()` method
3. Create HTML generator: `_generate_new_section()`
4. Add to `generate_html()` method

### Change Intelligence Rules

Modify these methods to adjust content detection:
- `_parse_assessment_findings()` - Physical/wound/IV parsing
- `_extract_wound_details()` - Wound status extraction
- `_extract_iv_details()` - IV site details
- `_parse_education()` - Education topic categorization

## Advanced Usage

### Programmatic Usage

```python
from nursing_narrative_converter import NursingNarrativeConverter

# Read markdown
with open('narrative.md', 'r') as f:
    content = f.read()

# Convert
converter = NursingNarrativeConverter(content)
converter.parse_markdown()
html = converter.generate_html('output.html')

# Or get HTML string without saving
html_string = converter.generate_html()
```

### Custom Template

```python
# Modify patient info before generation
converter.patient_info['demographics'] = "Custom demographics"
converter.patient_info['pmh'].append("New condition")

# Modify sections
converter.sections['focus_of_care']['objectives'].append({
    'title': 'Custom Objective',
    'desc': 'Custom description'
})

# Generate with modifications
converter.generate_html('custom_output.html')
```

## Troubleshooting

### Issue: Sections not parsing correctly

**Solution:** Check that section headers match exactly:
- `**Visit Summary:**` (with bold and colon)
- `**Focus of Care:**`
- `**Homebound Status:**`
- `**Education Provided:**`

### Issue: Patient history not displaying

**Solution:** Ensure PMH is comma-separated:
```markdown
**Past Medical History: Condition 1, Condition 2, Condition 3**
```

### Issue: Bullet points not rendering

**Solution:** Use proper markdown bullets:
- Start with `•`, `-`, or `*`
- Include space after bullet marker
- One bullet per line

### Issue: Special characters displaying incorrectly

**Solution:** Save markdown file with UTF-8 encoding

## Examples

### Example 1: Basic Conversion
```bash
python nursing_narrative_converter.py patient_notes.md
# Output: patient_notes_structured.html
```

### Example 2: Custom Output Location
```bash
python nursing_narrative_converter.py notes.md /reports/patient_001.html
```

### Example 3: Batch Processing
```bash
python batch_convert_narratives.py ./nursing_notes ./html_reports
```

## File Structure

```
nursing-narrative-converter/
├── nursing_narrative_converter.py   # Main converter script
├── batch_convert_narratives.py      # Batch processing script
├── README.md                         # This file
└── examples/
    ├── sample_narrative.md           # Example input
    └── sample_output.html            # Example output
```

## Requirements

- Python 3.6 or higher
- No external dependencies

## License

MIT License - Free to use and modify for your nursing documentation needs.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review example files
3. Verify markdown format matches expected structure

## Version History

**v1.0.0** (2025-10-30)
- Initial release
- Automatic section parsing
- Professional HTML generation
- Batch processing support
- Smart content detection

## Credits

Created by AISim for automated nursing documentation.
Designed for Recipe Labs medical documentation workflows.
