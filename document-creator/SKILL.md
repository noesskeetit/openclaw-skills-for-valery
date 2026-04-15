---
name: document-creator
description: "Use this skill when the user wants to create, edit, or manipulate office documents and PDFs — Word (.docx), Excel (.xlsx, .xlsm, .csv), PowerPoint (.pptx), PDF. Triggers: any mention of documents, spreadsheets, presentations, slides, decks, reports, memos, letters, or PDFs; producing professional documents with formatting; extracting or reorganizing content; filling PDF forms; merging/splitting PDFs; creating charts or tables in Excel; building slide decks. Do NOT use for Google Docs/Sheets or general coding tasks unrelated to document generation."
license: MIT
---

# Document Creator

## Requirements

- **System (required):** `python3`, `poppler-utils`
- **System (optional):** `node` (for `docx`/`pptxgenjs`/`pdf-lib`/`sharp` workflows), `pandoc`, `libreoffice` (writer/calc/impress) — needed for `recalc.py`, `soffice.py`, `accept_changes.py` and DOCX→other-format conversion
- **Python:** see `requirements.txt`
- **npm (optional):** `docx`, `pptxgenjs`, `pdf-lib`, `sharp` — only when using the JS workflows documented below

Skill for creating, editing, and analyzing office documents: DOCX, XLSX, PPTX, and PDF.

---

# DOCX: Word Documents

## Overview

A .docx file is a ZIP archive containing XML files.

## Quick Reference

| Task | Approach |
|------|----------|
| Read/analyze content | `pandoc` or unpack for raw XML |
| Create new document | Use `docx-js` - see Creating New Documents below |
| Edit existing document | Unpack → edit XML → repack - see Editing Existing Documents below |

### Converting .doc to .docx

Legacy `.doc` files must be converted before editing:

```bash
python scripts/office/soffice.py --headless --convert-to docx document.doc
```

### Reading Content

```bash
# Text extraction with tracked changes
pandoc --track-changes=all document.docx -o output.md

# Raw XML access
python scripts/office/unpack.py document.docx unpacked/
```

### Converting to Images

```bash
python scripts/office/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

### Accepting Tracked Changes

To produce a clean document with all tracked changes accepted (requires LibreOffice):

```bash
python scripts/accept_changes.py input.docx output.docx
```

---

## Creating New Documents

Generate .docx files with JavaScript, then validate. Install: `npm install -g docx`

### Setup
```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,
        InternalHyperlink, Bookmark, FootnoteReferenceRun, PositionalTab,
        PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,
        TabStopType, TabStopPosition, Column, SectionType,
        TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, PageBreak } = require('docx');

const doc = new Document({ sections: [{ children: [/* content */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer));
```

### Validation
After creating the file, validate it. If validation fails, unpack, fix the XML, and repack.
```bash
python scripts/office/validate.py doc.docx
```

### Page Size

```javascript
// CRITICAL: docx-js defaults to A4, not US Letter
// Always set page size explicitly for consistent results
sections: [{
  properties: {
    page: {
      size: {
        width: 12240,   // 8.5 inches in DXA
        height: 15840   // 11 inches in DXA
      },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch margins
    }
  },
  children: [/* content */]
}]
```

**Common page sizes (DXA units, 1440 DXA = 1 inch):**

| Paper | Width | Height | Content Width (1" margins) |
|-------|-------|--------|---------------------------|
| US Letter | 12,240 | 15,840 | 9,360 |
| A4 (default) | 11,906 | 16,838 | 9,026 |

**Landscape orientation:** docx-js swaps width/height internally, so pass portrait dimensions and let it handle the swap:
```javascript
size: {
  width: 12240,   // Pass SHORT edge as width
  height: 15840,  // Pass LONG edge as height
  orientation: PageOrientation.LANDSCAPE  // docx-js swaps them in the XML
},
// Content width = 15840 - left margin - right margin (uses the long edge)
```

### Styles (Override Built-in Headings)

Use Arial as the default font (universally supported). Keep titles black for readability.

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }, // 12pt default
    paragraphStyles: [
      // IMPORTANT: Use exact IDs to override built-in styles
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } }, // outlineLevel required for TOC
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Title")] }),
    ]
  }]
});
```

### Lists (NEVER use unicode bullets)

```javascript
// WRONG - never manually insert bullet characters
new Paragraph({ children: [new TextRun("* Item")] })  // BAD
new Paragraph({ children: [new TextRun("\u2022 Item")] })  // BAD

// CORRECT - use numbering config with LevelFormat.BULLET
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "*", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("Bullet item")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 },
        children: [new TextRun("Numbered item")] }),
    ]
  }]
});

// Each reference creates INDEPENDENT numbering
// Same reference = continues (1,2,3 then 4,5,6)
// Different reference = restarts (1,2,3 then 1,2,3)
```

### Tables

**CRITICAL: Tables need dual widths** - set both `columnWidths` on the table AND `width` on each cell. Without both, tables render incorrectly on some platforms.

```javascript
// CRITICAL: Always set table width for consistent rendering
// CRITICAL: Use ShadingType.CLEAR (not SOLID) to prevent black backgrounds
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

new Table({
  width: { size: 9360, type: WidthType.DXA }, // Always use DXA (percentages break in Google Docs)
  columnWidths: [4680, 4680], // Must sum to table width (DXA: 1440 = 1 inch)
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: 4680, type: WidthType.DXA }, // Also set on each cell
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, // CLEAR not SOLID
          margins: { top: 80, bottom: 80, left: 120, right: 120 }, // Cell padding (internal, not added to width)
          children: [new Paragraph({ children: [new TextRun("Cell")] })]
        })
      ]
    })
  ]
})
```

**Table width calculation:**

Always use `WidthType.DXA` -- `WidthType.PERCENTAGE` breaks in Google Docs.

```javascript
// Table width = sum of columnWidths = content width
// US Letter with 1" margins: 12240 - 2880 = 9360 DXA
width: { size: 9360, type: WidthType.DXA },
columnWidths: [7000, 2360]  // Must sum to table width
```

**Width rules:**
- **Always use `WidthType.DXA`** -- never `WidthType.PERCENTAGE` (incompatible with Google Docs)
- Table width must equal the sum of `columnWidths`
- Cell `width` must match corresponding `columnWidth`
- Cell `margins` are internal padding - they reduce content area, not add to cell width
- For full-width tables: use content width (page width minus left and right margins)

### Images

```javascript
// CRITICAL: type parameter is REQUIRED
new Paragraph({
  children: [new ImageRun({
    type: "png", // Required: png, jpg, jpeg, gif, bmp, svg
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150 },
    altText: { title: "Title", description: "Desc", name: "Name" } // All three required
  })]
})
```

### Page Breaks

```javascript
// CRITICAL: PageBreak must be inside a Paragraph
new Paragraph({ children: [new PageBreak()] })

// Or use pageBreakBefore
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
```

### Hyperlinks

```javascript
// External link
new Paragraph({
  children: [new ExternalHyperlink({
    children: [new TextRun({ text: "Click here", style: "Hyperlink" })],
    link: "https://example.com",
  })]
})

// Internal link (bookmark + reference)
// 1. Create bookmark at destination
new Paragraph({ heading: HeadingLevel.HEADING_1, children: [
  new Bookmark({ id: "chapter1", children: [new TextRun("Chapter 1")] }),
]})
// 2. Link to it
new Paragraph({ children: [new InternalHyperlink({
  children: [new TextRun({ text: "See Chapter 1", style: "Hyperlink" })],
  anchor: "chapter1",
})]})
```

### Footnotes

```javascript
const doc = new Document({
  footnotes: {
    1: { children: [new Paragraph("Source: Annual Report 2024")] },
    2: { children: [new Paragraph("See appendix for methodology")] },
  },
  sections: [{
    children: [new Paragraph({
      children: [
        new TextRun("Revenue grew 15%"),
        new FootnoteReferenceRun(1),
        new TextRun(" using adjusted metrics"),
        new FootnoteReferenceRun(2),
      ],
    })]
  }]
});
```

### Tab Stops

```javascript
// Right-align text on same line (e.g., date opposite a title)
new Paragraph({
  children: [
    new TextRun("Company Name"),
    new TextRun("\tJanuary 2025"),
  ],
  tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
})

// Dot leader (e.g., TOC-style)
new Paragraph({
  children: [
    new TextRun("Introduction"),
    new TextRun({ children: [
      new PositionalTab({
        alignment: PositionalTabAlignment.RIGHT,
        relativeTo: PositionalTabRelativeTo.MARGIN,
        leader: PositionalTabLeader.DOT,
      }),
      "3",
    ]}),
  ],
})
```

### Multi-Column Layouts

```javascript
// Equal-width columns
sections: [{
  properties: {
    column: {
      count: 2,          // number of columns
      space: 720,        // gap between columns in DXA (720 = 0.5 inch)
      equalWidth: true,
      separate: true,    // vertical line between columns
    },
  },
  children: [/* content flows naturally across columns */]
}]

// Custom-width columns (equalWidth must be false)
sections: [{
  properties: {
    column: {
      equalWidth: false,
      children: [
        new Column({ width: 5400, space: 720 }),
        new Column({ width: 3240 }),
      ],
    },
  },
  children: [/* content */]
}]
```

Force a column break with a new section using `type: SectionType.NEXT_COLUMN`.

### Table of Contents

```javascript
// CRITICAL: Headings must use HeadingLevel ONLY - no custom styles
new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" })
```

### Headers/Footers

```javascript
sections: [{
  properties: {
    page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } // 1440 = 1 inch
  },
  headers: {
    default: new Header({ children: [new Paragraph({ children: [new TextRun("Header")] })] })
  },
  footers: {
    default: new Footer({ children: [new Paragraph({
      children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })]
    })] })
  },
  children: [/* content */]
}]
```

### Critical Rules for docx-js

- **Set page size explicitly** - docx-js defaults to A4; use US Letter (12240 x 15840 DXA) for US documents
- **Landscape: pass portrait dimensions** - docx-js swaps width/height internally; pass short edge as `width`, long edge as `height`, and set `orientation: PageOrientation.LANDSCAPE`
- **Never use `\n`** - use separate Paragraph elements
- **Never use unicode bullets** - use `LevelFormat.BULLET` with numbering config
- **PageBreak must be in Paragraph** - standalone creates invalid XML
- **ImageRun requires `type`** - always specify png/jpg/etc
- **Always set table `width` with DXA** - never use `WidthType.PERCENTAGE` (breaks in Google Docs)
- **Tables need dual widths** - `columnWidths` array AND cell `width`, both must match
- **Table width = sum of columnWidths** - for DXA, ensure they add up exactly
- **Always add cell margins** - use `margins: { top: 80, bottom: 80, left: 120, right: 120 }` for readable padding
- **Use `ShadingType.CLEAR`** - never SOLID for table shading
- **Never use tables as dividers/rules** - cells have minimum height and render as empty boxes (including in headers/footers); use `border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 1 } }` on a Paragraph instead. For two-column footers, use tab stops (see Tab Stops section), not tables
- **TOC requires HeadingLevel only** - no custom styles on heading paragraphs
- **Override built-in styles** - use exact IDs: "Heading1", "Heading2", etc.
- **Include `outlineLevel`** - required for TOC (0 for H1, 1 for H2, etc.)

---

## Editing Existing Documents

**Follow all 3 steps in order.**

### Step 1: Unpack
```bash
python scripts/office/unpack.py document.docx unpacked/
```
Extracts XML, pretty-prints, merges adjacent runs, and converts smart quotes to XML entities (`&#x201C;` etc.) so they survive editing. Use `--merge-runs false` to skip run merging.

### Step 2: Edit XML

Edit files in `unpacked/word/`. See XML Reference below for patterns.

**Use "Claude" as the author** for tracked changes and comments, unless the user explicitly requests use of a different name.

**Use the Edit tool directly for string replacement. Do not write Python scripts.** Scripts introduce unnecessary complexity. The Edit tool shows exactly what is being replaced.

**CRITICAL: Use smart quotes for new content.** When adding text with apostrophes or quotes, use XML entities to produce smart quotes:
```xml
<!-- Use these entities for professional typography -->
<w:t>Here&#x2019;s a quote: &#x201C;Hello&#x201D;</w:t>
```
| Entity | Character |
|--------|-----------|
| `&#x2018;` | ' (left single) |
| `&#x2019;` | ' (right single / apostrophe) |
| `&#x201C;` | " (left double) |
| `&#x201D;` | " (right double) |

**Adding comments:** Use `comment.py` to handle boilerplate across multiple XML files (text must be pre-escaped XML):
```bash
python scripts/comment.py unpacked/ 0 "Comment text with &amp; and &#x2019;"
python scripts/comment.py unpacked/ 1 "Reply text" --parent 0  # reply to comment 0
python scripts/comment.py unpacked/ 0 "Text" --author "Custom Author"  # custom author name
```
Then add markers to document.xml (see Comments in XML Reference).

### Step 3: Pack
```bash
python scripts/office/pack.py unpacked/ output.docx --original document.docx
```
Validates with auto-repair, condenses XML, and creates DOCX. Use `--validate false` to skip.

**Auto-repair will fix:**
- `durableId` >= 0x7FFFFFFF (regenerates valid ID)
- Missing `xml:space="preserve"` on `<w:t>` with whitespace

**Auto-repair won't fix:**
- Malformed XML, invalid element nesting, missing relationships, schema violations

### Common Pitfalls

- **Replace entire `<w:r>` elements**: When adding tracked changes, replace the whole `<w:r>...</w:r>` block with `<w:del>...<w:ins>...` as siblings. Don't inject tracked change tags inside a run.
- **Preserve `<w:rPr>` formatting**: Copy the original run's `<w:rPr>` block into your tracked change runs to maintain bold, font size, etc.

---

## DOCX XML Reference

### Schema Compliance

- **Element order in `<w:pPr>`**: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` last
- **Whitespace**: Add `xml:space="preserve"` to `<w:t>` with leading/trailing spaces
- **RSIDs**: Must be 8-digit hex (e.g., `00AB1234`)

### Tracked Changes

**Insertion:**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

**Deletion:**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

**Inside `<w:del>`**: Use `<w:delText>` instead of `<w:t>`, and `<w:delInstrText>` instead of `<w:instrText>`.

**Minimal edits** - only mark what changes:
```xml
<!-- Change "30 days" to "60 days" -->
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Claude" w:date="...">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Claude" w:date="...">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

**Deleting entire paragraphs/list items** - when removing ALL content from a paragraph, also mark the paragraph mark as deleted so it merges with the next paragraph. Add `<w:del/>` inside `<w:pPr><w:rPr>`:
```xml
<w:p>
  <w:pPr>
    <w:numPr>...</w:numPr>  <!-- list numbering if present -->
    <w:rPr>
      <w:del w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z"/>
    </w:rPr>
  </w:pPr>
  <w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
    <w:r><w:delText>Entire paragraph content being deleted...</w:delText></w:r>
  </w:del>
</w:p>
```
Without the `<w:del/>` in `<w:pPr><w:rPr>`, accepting changes leaves an empty paragraph/list item.

**Rejecting another author's insertion** - nest deletion inside their insertion:
```xml
<w:ins w:author="Jane" w:id="5">
  <w:del w:author="Claude" w:id="10">
    <w:r><w:delText>their inserted text</w:delText></w:r>
  </w:del>
</w:ins>
```

**Restoring another author's deletion** - add insertion after (don't modify their deletion):
```xml
<w:del w:author="Jane" w:id="5">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
<w:ins w:author="Claude" w:id="10">
  <w:r><w:t>deleted text</w:t></w:r>
</w:ins>
```

### Comments

After running `comment.py` (see Step 2), add markers to document.xml. For replies, use `--parent` flag and nest markers inside the parent's.

**CRITICAL: `<w:commentRangeStart>` and `<w:commentRangeEnd>` are siblings of `<w:r>`, never inside `<w:r>`.**

```xml
<!-- Comment markers are direct children of w:p, never inside w:r -->
<w:commentRangeStart w:id="0"/>
<w:del w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted</w:delText></w:r>
</w:del>
<w:r><w:t> more text</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>

<!-- Comment 0 with reply 1 nested inside -->
<w:commentRangeStart w:id="0"/>
  <w:commentRangeStart w:id="1"/>
  <w:r><w:t>text</w:t></w:r>
  <w:commentRangeEnd w:id="1"/>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="1"/></w:r>
```

### Images

1. Add image file to `word/media/`
2. Add relationship to `word/_rels/document.xml.rels`:
```xml
<Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
```
3. Add content type to `[Content_Types].xml`:
```xml
<Default Extension="png" ContentType="image/png"/>
```
4. Reference in document.xml:
```xml
<w:drawing>
  <wp:inline>
    <wp:extent cx="914400" cy="914400"/>  <!-- EMUs: 914400 = 1 inch -->
    <a:graphic>
      <a:graphicData uri=".../picture">
        <pic:pic>
          <pic:blipFill><a:blip r:embed="rId5"/></pic:blipFill>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```

---

## DOCX Dependencies

- **pandoc**: Text extraction
- **docx**: `npm install -g docx` (new documents)
- **LibreOffice**: PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- **Poppler**: `pdftoppm` for images

---

# XLSX: Excel Spreadsheets

## Requirements for Outputs

### All Excel files

#### Professional Font
- Use a consistent, professional font (e.g., Arial, Times New Roman) for all deliverables unless otherwise instructed by the user

#### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

#### Preserve Existing Templates (when updating templates)
- Study and EXACTLY match existing format, style, and conventions when modifying files
- Never impose standardized formatting on files with established patterns
- Existing template conventions ALWAYS override these guidelines

### Financial models

#### Color Coding Standards
Unless otherwise stated by the user or existing template

**Industry-Standard Color Conventions:**
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, and numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention or cells that need to be updated

#### Number Formatting Standards

- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use $#,##0 format; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., "$#,##0;($#,##0);-")
- **Percentages**: Default to 0.0% format (one decimal)
- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

#### Formula Construction Rules

- Place ALL assumptions (growth rates, margins, multiples, etc.) in separate assumption cells
- Use cell references instead of hardcoded values in formulas
- Example: Use =B5*(1+$B$6) instead of =B5*1.05

#### Formula Error Prevention
- Verify all cell references are correct
- Check for off-by-one errors in ranges
- Ensure consistent formulas across all projection periods
- Test with edge cases (zero values, negative numbers)
- Verify no unintended circular references

#### Documentation Requirements for Hardcodes
- Comment or in cells beside (if end of table). Format: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"
- Examples:
  - "Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"
  - "Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"

---

## Overview

A user may ask you to create, edit, or analyze the contents of an .xlsx file. You have different tools and workflows available for different tasks.

## Important Requirements

**LibreOffice Required for Formula Recalculation**: You can assume LibreOffice is installed for recalculating formula values using the `scripts/recalc.py` script. The script automatically configures LibreOffice on first run, including in sandboxed environments where Unix sockets are restricted (handled by `scripts/office/soffice.py`)

## Reading and analyzing data

### Data analysis with pandas
For data analysis, visualization, and basic operations, use **pandas** which provides powerful data manipulation capabilities:

```python
import pandas as pd

# Read Excel
df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

# Analyze
df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics

# Write Excel
df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.** This ensures the spreadsheet remains dynamic and updateable.

### WRONG - Hardcoding Calculated Values
```python
# Bad: Calculating in Python and hardcoding result
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000

# Bad: Computing growth rate in Python
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # Hardcodes 0.15
```

### CORRECT - Using Excel Formulas
```python
# Good: Let Excel calculate the sum
sheet['B10'] = '=SUM(B2:B9)'

# Good: Growth rate as Excel formula
sheet['C5'] = '=(C4-C2)/C2'

# Good: Average using Excel function
sheet['D20'] = '=AVERAGE(D2:D19)'
```

This applies to ALL calculations - totals, percentages, ratios, differences, etc. The spreadsheet should be able to recalculate when source data changes.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: Use the scripts/recalc.py script
   ```bash
   python scripts/recalc.py output.xlsx
   ```
6. **Verify and fix any errors**:
   - The script returns JSON with error details
   - If `status` is `errors_found`, check `error_summary` for specific error types and locations
   - Fix the identified errors and recalculate again
   - Common errors to fix:
     - `#REF!`: Invalid cell references
     - `#DIV/0!`: Division by zero
     - `#VALUE!`: Wrong data type in formula
     - `#NAME?`: Unrecognized formula name

### Creating new Excel files

```python
# Using openpyxl for formulas and formatting
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# Add data
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# Add formula
sheet['B2'] = '=SUM(A1:A10)'

# Formatting
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# Column width
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### Editing existing Excel files

```python
# Using openpyxl to preserve formulas and formatting
from openpyxl import load_workbook

# Load existing file
wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName'] for specific sheet

# Working with multiple sheets
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

# Modify cells
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # Insert row at position 2
sheet.delete_cols(3)  # Delete column 3

# Add new sheet
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## Recalculating formulas

Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `scripts/recalc.py` script to recalculate formulas:

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

Example:
```bash
python scripts/recalc.py output.xlsx 30
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors (#REF!, #DIV/0!, etc.)
- Returns JSON with detailed error locations and counts
- Works on both Linux and macOS

## Formula Verification Checklist

### Essential Verification
- [ ] **Test 2-3 sample references**: Verify they pull correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] **Row offset**: Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)

### Common Pitfalls
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Far-right columns**: FY data often in columns 50+
- [ ] **Multiple matches**: Search all occurrences, not just first
- [ ] **Division by zero**: Check denominators before using `/` in formulas (#DIV/0!)
- [ ] **Wrong references**: Verify all cell references point to intended cells (#REF!)
- [ ] **Cross-sheet references**: Use correct format (Sheet1!A1) for linking sheets

### Interpreting scripts/recalc.py Output
The script returns JSON with error details:
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {}
}
```

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost
- For large files: Use `read_only=True` for reading or `write_only=True` for writing
- Formulas are preserved but not evaluated - use scripts/recalc.py to update values

### Working with pandas
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

### Code Style Guidelines
**IMPORTANT**: When generating Python code for Excel operations:
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations

**For Excel files themselves**:
- Add comments to cells with complex formulas or important assumptions
- Document data sources for hardcoded values

---

# PPTX: PowerPoint Presentations

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | See Editing Workflow below |
| Create from scratch | See PptxGenJS Reference below |

---

## Reading Content

```bash
# Text extraction (.pptx only)
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

### Template-Based Workflow

When using an existing presentation as a template:

1. **Analyze existing slides**:
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```
   Review `thumbnails.jpg` to see layouts, and markitdown output to see placeholder text.

2. **Plan slide mapping**: For each content section, choose a template slide.

   **USE VARIED LAYOUTS** -- monotonous presentations are a common failure mode. Don't default to basic title + bullet slides. Actively seek out:
   - Multi-column layouts (2-column, 3-column)
   - Image + text combinations
   - Full-bleed images with text overlay
   - Quote or callout slides
   - Section dividers
   - Stat/number callouts
   - Icon grids or icon + text rows

3. **Unpack**: `python scripts/office/unpack.py template.pptx unpacked/`

4. **Build presentation** (do this yourself, not with subagents):
   - Delete unwanted slides (remove from `<p:sldIdLst>`)
   - Duplicate slides you want to reuse (`add_slide.py`)
   - Reorder slides in `<p:sldIdLst>`
   - **Complete all structural changes before step 5**

5. **Edit content**: Update text in each `slide{N}.xml`.
   **Use subagents here if available** -- slides are separate XML files, so subagents can edit in parallel.

6. **Clean**: `python scripts/clean.py unpacked/`

7. **Pack**: `python scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/office/unpack.py` | Extract and pretty-print PPTX |
| `scripts/add_slide.py` | Duplicate slide or create from layout |
| `scripts/clean.py` | Remove orphaned files |
| `scripts/office/pack.py` | Repack with validation |
| `scripts/thumbnail.py` | Create visual grid of slides |

#### add_slide.py

```bash
python scripts/add_slide.py unpacked/ slide2.xml      # Duplicate slide
python scripts/add_slide.py unpacked/ slideLayout2.xml # From layout
```

Prints `<p:sldId>` to add to `<p:sldIdLst>` at desired position.

#### clean.py

```bash
python scripts/clean.py unpacked/
```

Removes slides not in `<p:sldIdLst>`, unreferenced media, orphaned rels.

### Slide Operations

Slide order is in `ppt/presentation.xml` -> `<p:sldIdLst>`.

**Reorder**: Rearrange `<p:sldId>` elements.

**Delete**: Remove `<p:sldId>`, then run `clean.py`.

**Add**: Use `add_slide.py`. Never manually copy slide files -- the script handles notes references, Content_Types.xml, and relationship IDs that manual copying misses.

### Editing Content

For each slide:
1. Read the slide's XML
2. Identify ALL placeholder content -- text, images, charts, icons, captions
3. Replace each placeholder with final content

**Use the Edit tool, not sed or Python scripts.** The Edit tool forces specificity about what to replace and where.

#### Formatting Rules

- **Bold all headers, subheadings, and inline labels**: Use `b="1"` on `<a:rPr>`. This includes slide titles, section headers, inline labels like "Status:", "Description:" at the start of a line.
- **Never use unicode bullets**: Use proper list formatting with `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency**: Let bullets inherit from the layout. Only specify `<a:buChar>` or `<a:buNone>`.

### Common Pitfalls

**Template Adaptation:**
- When source content has fewer items than the template, **remove excess elements entirely** (images, shapes, text boxes), don't just clear text
- **Template slots != Source items**: If template has 4 team members but source has 3, delete the 4th member's entire group (image + text boxes), not just the text
- When replacing text with different length content, test with visual QA after text changes

**Multi-Item Content:**
If source has multiple items, create separate `<a:p>` elements for each -- **never concatenate into one string**.

**WRONG** -- all items in one paragraph:
```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**CORRECT** -- separate paragraphs with bold headers:
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
```

**Smart Quotes:** Handled automatically by unpack/pack, but the Edit tool converts smart quotes to ASCII. When adding new text with quotes, use XML entities:
```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| Character | Name | XML Entity |
|-----------|------|------------|
| \u201C | Left double quote | `&#x201C;` |
| \u201D | Right double quote | `&#x201D;` |
| \u2018 | Left single quote | `&#x2018;` |
| \u2019 | Right single quote | `&#x2019;` |

**Other:**
- **Whitespace**: Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **XML parsing**: Use `defusedxml.minidom`, not `xml.etree.ElementTree` (corrupts namespaces)

---

## Creating from Scratch with PptxGenJS

Use when no template or reference presentation is available.

### Setup & Basic Structure

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';  // or 'LAYOUT_16x10', 'LAYOUT_4x3', 'LAYOUT_WIDE'
pres.author = 'Your Name';
pres.title = 'Presentation Title';

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "Presentation.pptx" });
```

### Layout Dimensions

Slide dimensions (coordinates in inches):
- `LAYOUT_16x9`: 10" x 5.625" (default)
- `LAYOUT_16x10`: 10" x 6.25"
- `LAYOUT_4x3`: 10" x 7.5"
- `LAYOUT_WIDE`: 13.3" x 7.5"

### Text & Formatting

```javascript
// Basic text
slide.addText("Simple Text", {
  x: 1, y: 1, w: 8, h: 2, fontSize: 24, fontFace: "Arial",
  color: "363636", bold: true, align: "center", valign: "middle"
});

// Character spacing (use charSpacing, not letterSpacing which is silently ignored)
slide.addText("SPACED TEXT", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });

// Rich text arrays
slide.addText([
  { text: "Bold ", options: { bold: true } },
  { text: "Italic ", options: { italic: true } }
], { x: 1, y: 3, w: 8, h: 1 });

// Multi-line text (requires breakLine: true)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }  // Last item doesn't need breakLine
], { x: 0.5, y: 0.5, w: 8, h: 2 });

// Text box margin (internal padding)
slide.addText("Title", {
  x: 0.5, y: 0.3, w: 9, h: 0.6,
  margin: 0  // Use 0 when aligning text with other elements like shapes or icons
});
```

**Tip:** Text boxes have internal margin by default. Set `margin: 0` when you need text to align precisely with shapes, lines, or icons at the same x-position.

### Lists & Bullets

```javascript
// CORRECT: Multiple bullets
slide.addText([
  { text: "First item", options: { bullet: true, breakLine: true } },
  { text: "Second item", options: { bullet: true, breakLine: true } },
  { text: "Third item", options: { bullet: true } }
], { x: 0.5, y: 0.5, w: 8, h: 3 });

// WRONG: Never use unicode bullets
slide.addText("* First item", { ... });  // Creates double bullets

// Sub-items and numbered lists
{ text: "Sub-item", options: { bullet: true, indentLevel: 1 } }
{ text: "First", options: { bullet: { type: "number" }, breakLine: true } }
```

### Shapes

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 1.5, h: 3.0,
  fill: { color: "FF0000" }, line: { color: "000000", width: 2 }
});

slide.addShape(pres.shapes.OVAL, { x: 4, y: 1, w: 2, h: 2, fill: { color: "0000FF" } });

slide.addShape(pres.shapes.LINE, {
  x: 1, y: 3, w: 5, h: 0, line: { color: "FF0000", width: 3, dashType: "dash" }
});

// With transparency
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "0088CC", transparency: 50 }
});

// Rounded rectangle (rectRadius only works with ROUNDED_RECTANGLE, not RECTANGLE)
// Don't pair with rectangular accent overlays -- they won't cover rounded corners. Use RECTANGLE instead.
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" }, rectRadius: 0.1
});

// With shadow
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" },
  shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 }
});
```

Shadow options:

| Property | Type | Range | Notes |
|----------|------|-------|-------|
| `type` | string | `"outer"`, `"inner"` | |
| `color` | string | 6-char hex (e.g. `"000000"`) | No `#` prefix, no 8-char hex -- see Common Pitfalls |
| `blur` | number | 0-100 pt | |
| `offset` | number | 0-200 pt | **Must be non-negative** -- negative values corrupt the file |
| `angle` | number | 0-359 degrees | Direction the shadow falls (135 = bottom-right, 270 = upward) |
| `opacity` | number | 0.0-1.0 | Use this for transparency, never encode in color string |

To cast a shadow upward (e.g. on a footer bar), use `angle: 270` with a positive offset -- do **not** use a negative offset.

**Note**: Gradient fills are not natively supported. Use a gradient image as a background instead.

### Images

```javascript
// From file path
slide.addImage({ path: "images/chart.png", x: 1, y: 1, w: 5, h: 3 });

// From URL
slide.addImage({ path: "https://example.com/image.jpg", x: 1, y: 1, w: 5, h: 3 });

// From base64 (faster, no file I/O)
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });
```

Image options:
```javascript
slide.addImage({
  path: "image.png",
  x: 1, y: 1, w: 5, h: 3,
  rotate: 45,              // 0-359 degrees
  rounding: true,          // Circular crop
  transparency: 50,        // 0-100
  altText: "Description",  // Accessibility
  hyperlink: { url: "https://example.com" }
});
```

Image sizing modes:
```javascript
// Contain - fit inside, preserve ratio
{ sizing: { type: 'contain', w: 4, h: 3 } }

// Cover - fill area, preserve ratio (may crop)
{ sizing: { type: 'cover', w: 4, h: 3 } }
```

### Calculate Dimensions (preserve aspect ratio)

```javascript
const origWidth = 1978, origHeight = 923, maxHeight = 3.0;
const calcWidth = maxHeight * (origWidth / origHeight);
const centerX = (10 - calcWidth) / 2;

slide.addImage({ path: "image.png", x: centerX, y: 1.2, w: calcWidth, h: maxHeight });
```

### Icons

Use react-icons to generate SVG icons, then rasterize to PNG for universal compatibility.

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle, FaChartLine } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

// Add icon to slide
const iconData = await iconToBase64Png(FaCheckCircle, "#4472C4", 256);
slide.addImage({ data: iconData, x: 1, y: 1, w: 0.5, h: 0.5 });
```

**Note**: Use size 256 or higher for crisp icons. Install: `npm install -g react-icons react react-dom sharp`

### Slide Backgrounds

```javascript
// Solid color
slide.background = { color: "F1F1F1" };

// Image from URL
slide.background = { path: "https://example.com/bg.jpg" };

// Image from base64
slide.background = { data: "image/png;base64,iVBORw0KGgo..." };
```

### Tables

```javascript
slide.addTable([
  ["Header 1", "Header 2"],
  ["Cell 1", "Cell 2"]
], {
  x: 1, y: 1, w: 8, h: 2,
  border: { pt: 1, color: "999999" }, fill: { color: "F1F1F1" }
});

// Advanced with merged cells
let tableData = [
  [{ text: "Header", options: { fill: { color: "6699CC" }, color: "FFFFFF", bold: true } }, "Cell"],
  [{ text: "Merged", options: { colspan: 2 } }]
];
slide.addTable(tableData, { x: 1, y: 3.5, w: 8, colW: [4, 4] });
```

### Charts

```javascript
// Bar chart
slide.addChart(pres.charts.BAR, [{
  name: "Sales", labels: ["Q1", "Q2", "Q3", "Q4"], values: [4500, 5500, 6200, 7100]
}], {
  x: 0.5, y: 0.6, w: 6, h: 3, barDir: 'col',
  showTitle: true, title: 'Quarterly Sales'
});

// Line chart
slide.addChart(pres.charts.LINE, [{
  name: "Temp", labels: ["Jan", "Feb", "Mar"], values: [32, 35, 42]
}], { x: 0.5, y: 4, w: 6, h: 3, lineSize: 3, lineSmooth: true });

// Pie chart
slide.addChart(pres.charts.PIE, [{
  name: "Share", labels: ["A", "B", "Other"], values: [35, 45, 20]
}], { x: 7, y: 1, w: 5, h: 4, showPercent: true });
```

#### Better-Looking Charts

Default charts look dated. Apply these options for a modern, clean appearance:

```javascript
slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 1, w: 9, h: 4, barDir: "col",

  // Custom colors (match your presentation palette)
  chartColors: ["0D9488", "14B8A6", "5EEAD4"],

  // Clean background
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },

  // Muted axis labels
  catAxisLabelColor: "64748B",
  valAxisLabelColor: "64748B",

  // Subtle grid (value axis only)
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },

  // Data labels on bars
  showValue: true,
  dataLabelPosition: "outEnd",
  dataLabelColor: "1E293B",

  // Hide legend for single series
  showLegend: false,
});
```

### Slide Masters

```javascript
pres.defineSlideMaster({
  title: 'TITLE_SLIDE', background: { color: '283A5E' },
  objects: [{
    placeholder: { options: { name: 'title', type: 'title', x: 1, y: 2, w: 8, h: 2 } }
  }]
});

let titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
titleSlide.addText("My Title", { placeholder: "title" });
```

### PptxGenJS Common Pitfalls

1. **NEVER use "#" with hex colors** - causes file corruption
   ```javascript
   color: "FF0000"      // CORRECT
   color: "#FF0000"     // WRONG
   ```

2. **NEVER encode opacity in hex color strings** - 8-char colors (e.g., `"00000020"`) corrupt the file. Use the `opacity` property instead.
   ```javascript
   shadow: { type: "outer", blur: 6, offset: 2, color: "00000020" }          // CORRUPTS FILE
   shadow: { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.12 }  // CORRECT
   ```

3. **Use `bullet: true`** - NEVER unicode symbols like "*" (creates double bullets)

4. **Use `breakLine: true`** between array items or text runs together

5. **Avoid `lineSpacing` with bullets** - causes excessive gaps; use `paraSpaceAfter` instead

6. **Each presentation needs fresh instance** - don't reuse `pptxgen()` objects

7. **NEVER reuse option objects across calls** - PptxGenJS mutates objects in-place (e.g. converting shadow values to EMU). Sharing one object between multiple calls corrupts the second shape.
   ```javascript
   const shadow = { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 };
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });  // WRONG: second call gets already-converted values
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });

   const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
   slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });  // CORRECT: fresh object each time
   slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });
   ```

8. **Don't use `ROUNDED_RECTANGLE` with accent borders** - rectangular overlay bars won't cover rounded corners. Use `RECTANGLE` instead.

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure).
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it -- rounded image frames, icons in colored circles, thick single-side borders.

### Color Palettes

Choose colors that match your topic -- don't default to generic blue:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** -- image, chart, icon, or shape.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid
- Half-bleed image with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons)
- Timeline or process flow (numbered steps, arrows)

### Typography

**Choose an interesting font pairing** -- don't default to Arial:

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room -- don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** -- vary columns, cards, and callouts across slides
- **Don't center body text** -- left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** -- titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** -- pick colors that reflect the specific topic
- **Don't create text-only slides** -- add images, icons, charts, or visual elements
- **Don't forget text box padding** -- when aligning lines or shapes with text edges, set `margin: 0` on the text box
- **Don't use low-contrast elements** -- icons AND text need strong contrast against the background
- **NEVER use accent lines under titles** -- these are a hallmark of AI-generated slides; use whitespace or background color instead

---

## PPTX QA (Required)

**Assume there are problems. Your job is to find them.**

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout"
```

### Visual QA

**USE SUBAGENTS** -- even for 2-3 slides.

Convert slides to images (see Converting to Images), then use this prompt:

```
Visually inspect these slides. Assume there are issues -- find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text or icons
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images -- run `ls -1 "$PWD"/slide-*.jpg` and use the exact absolute paths it prints:
1. <absolute-path>/slide-N.jpg -- (Expected: [brief description])
2. <absolute-path>/slide-N.jpg -- (Expected: [brief description])
...

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides -> Convert to images -> Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** -- one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

**Pass the absolute paths printed above directly to the view tool.** The `rm` clears stale images from prior runs. `pdftoppm` zero-pads based on page count: `slide-1.jpg` for decks under 10 pages, `slide-01.jpg` for 10-99, `slide-001.jpg` for 100+.

**After fixes, rerun all four commands above** -- the PDF must be regenerated from the edited `.pptx` before `pdftoppm` can reflect your changes.

---

## PPTX Dependencies

- `pip install "markitdown[pptx]"` - text extraction
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images

---

# PDF: PDF Processing

## Overview

This section covers essential PDF processing operations using Python libraries and command-line tools.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

c.drawString(100, height - 100, "Hello World!")
c.line(100, height - 140, 400, height - 140)
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

doc.build(story)
```

#### Subscripts and Superscripts

**IMPORTANT**: Never use Unicode subscript/superscript characters in ReportLab PDFs. The built-in fonts do not include these glyphs, causing them to render as solid black boxes.

Instead, use ReportLab's XML markup tags in Paragraph objects:
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Subscripts: use <sub> tag
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# Superscripts: use <super> tag
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')

text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## PDF Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
