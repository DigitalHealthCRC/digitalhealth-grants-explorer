# Grants Explorer - File Structure

## 📁 Essential Files (DO NOT DELETE)

### Web Application
- **`index.html`** - Main web page
- **`info.html`** - Information page
- **`style.css`** - Styling
- **`app.js`** - Application logic

### Data Files
- **`data.csv`** - Original grants data (manually maintained)
- **`data_parsed_complete.csv`** - Processed data used by web app (auto-generated)

### Processing Scripts
- **`preprocess_data.py`** - **RUN THIS** to update parsed data
  - Runs all preprocessing steps
  - Cleans up intermediate files
  - Single command: `python preprocess_data.py`

### Supporting Scripts (Used by preprocess_data.py)
- `parse_funding_amounts.py` - Parses funding amounts
- `parse_deadlines.py` - Parses application deadlines
- `merge_parsed_data.py` - Merges parsed data

### Analysis Scripts (Optional)
- `analyze_parsed_funding.py` - Generate funding statistics
- `tag_analysis.py` - Analyze grant tags
- `complexity.py` - Complexity analysis

## 🚀 Quick Start

### To Update Data:

1. **Edit** `data.csv` with new grants
2. **Run** preprocessing:
   ```bash
   python preprocess_data.py
   ```
3. **Refresh** browser (Ctrl+F5)

That's it! The website will automatically use the updated data.

## 📊 Data Flow

```
data.csv (manual edits)
    ↓
python preprocess_data.py
    ↓
data_parsed_complete.csv (auto-generated)
    ↓
Web app (index.html + app.js)
    ↓
Users see updated grants
```

## 🗑️ Files You Can Delete

These are temporary/intermediate files that get regenerated:
- `data_with_parsed_funding.csv` (intermediate)
- `data_with_parsed_deadlines.csv` (intermediate)
- Any `.md` documentation files (optional)

## 📝 Documentation Files

- `README.md` - Project overview
- `PROJECT_COMPLETE_SUMMARY.md` - Full project documentation
- `DEADLINE_PARSING_SUMMARY.md` - Deadline parsing details
- `INTEGRATION_SUMMARY.md` - Web app integration guide

## 🔧 Development Files

- `.git/` - Git repository
- `.github/` - GitHub configuration
- `.gitignore` - Git ignore rules
- `code.code-workspace` - VS Code workspace
- `extractor/` - Data extraction tools

## 📦 Other Data Files

- `grants_url.csv` - Grant URLs
- `grant links.xlsx` - Grant links spreadsheet

---

## 💡 Pro Tips

### Daily Workflow:
1. Update `data.csv` when you find new grants
2. Run `python preprocess_data.py` once
3. Refresh browser to see changes

### Don't Worry About:
- Intermediate CSV files (auto-deleted)
- Parsing confidence levels (handled automatically)
- Currency conversions (done automatically)
- Date formatting (handled automatically)

### Keep Clean:
- Only keep `data.csv` and `data_parsed_complete.csv`
- Delete intermediate files if they appear
- Run `preprocess_data.py` instead of individual scripts

---

**Last Updated**: 2025-12-09
