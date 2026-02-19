# 🚀 Quick Start Guide - Streamlit Recruitment Analyst

## 5-Minute Setup

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Create Environment File
Create `.env` in the project root with:
```env
GEMINI_API_KEY=your_key_here
EMAIL_SENDER=optional_email@gmail.com
EMAIL_PASSWORD=optional_app_password
```

Get your Gemini API key (free): https://aistudio.google.com/apikey

### Step 3: Generate Sample Data (Optional)
```powershell
python tests/generate_dataset.py
```

This creates `data/candidats_100_random.xlsx` with realistic test data.

### Step 4: Launch the App
```powershell
python run_app.py
```

Open `http://localhost:8501` in your browser.

---

## 📊 Using Sample Data

### Sample Workflow
1. **Upload**: Select `data/candidats_100_random.xlsx`
2. **Configure**: Manual entry
   - Skills: `Python, SQL, AWS`
   - Min Experience: 2 years
3. **Analyze**: Click "Run Analysis"
4. **View**: Select 10 candidates, filter by EXCELLENT/GOOD
5. **Export**: Download Excel or send email

---

## 🎯 Your Data Format

Expected columns (any language):
```
ENGLISH          FRANÇAIS
name        or   nom
email       or   email
years_exp   or   années_exp
skills      or   compétences
availability or  disponibilité
```

Example CSV:
```csv
nom,email,années_exp,compétences,disponibilité
Alice Durand,alice@test.com,5,"Python, SQL, AWS",Immédiat
Bob Martin,bob@test.com,3,"Java, Spring Boot",2024-03-15
```

---

## ⚡ Features at a Glance

| Feature | What It Does |
|---------|-------------|
| **File Upload** | CSV/Excel → Instant preview |
| **Auto-Detect Skills** | Paste job description → AI extracts skills |
| **KPI Analysis** | Score candidates based on experience, skills, availability |
| **AI Insights** | Gemini analyzes pool and recommends top talent |
| **Custom Selection** | Choose how many candidates (not just top 3!) |
| **Multi-Filter** | Tier, availability, skills match |
| **Export** | Excel, CSV, or Email |

---

## 🔧 Troubleshooting

**Problem**: App won't start
```powershell
# Verify Streamlit installed
pip install streamlit==1.32.0

# Try running directly
streamlit run app_streamlit.py
```

**Problem**: "GEMINI_API_KEY not found"
- Check `.env` exists in **project root** (same folder as `app_streamlit.py`)
- No quotes around key value

**Problem**: Candidates won't load
- Column names must be exact (see format above)
- Try sample file first: `tests/generate_dataset.py`

---

## 💡 Pro Tips

1. **Test with sample data first** - Easier to understand flow
2. **Use auto-detection** - Paste a real job posting to see how AI extracts skills
3. **Experiment with filters** - Try different tier combinations
4. **Export before closing** - Downloads go to your Downloads folder

---

## 📚 More Help

- Full guide: `STREAMLIT_GUIDE.md`
- Architecture: `ARCHITECTURE.md`
- Module docs: Check docstrings in `src/modules/`

---

**Ready? Let's hire smarter! 🎯**

```powershell
python run_app.py
```
