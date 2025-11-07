# File Converter - Streamlit Cloud Deployment

## 🚀 Quick Deploy to Streamlit Cloud

1. **Push to GitHub** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `FileConverter/streamlit_app.py`
   - Click "Deploy"

3. **Add Groq API Key**
   - In Streamlit Cloud dashboard, go to your app
   - Click "⚙️ Settings" → "Secrets"
   - Add:
     ```toml
     GROQ_API_KEY = "your-groq-api-key-here"
     ```
   - Save

4. **Wait for deployment** (3-5 minutes)
   - System packages will be installed from `packages.txt`
   - Python dependencies from `requirements.txt`
   - App will automatically start

## 📦 Files for Deployment

### Required Files
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System packages (LibreOffice, Tesseract)
- ✅ `runtime.txt` - Python version
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `FileConverter/streamlit_app.py` - Main app file

### What Gets Installed
**System Packages (from packages.txt):**
- LibreOffice (for office format conversions)
- Tesseract OCR (for scanned PDF conversion)
- Poppler utils (for PDF to image conversion)

**Python Packages (from requirements.txt):**
- Streamlit (web framework)
- Groq (AI processing)
- PyMuPDF, pdfplumber (PDF processing)
- python-docx (Word document creation)
- And all other dependencies...

## 🔧 Configuration

### Streamlit Settings (.streamlit/config.toml)
- Max upload size: 200 MB
- XSRF protection: Disabled (for file uploads)
- Headless mode: Enabled (for server deployment)

### Environment Variables (Secrets)
Set in Streamlit Cloud dashboard:
```toml
GROQ_API_KEY = "your-key"
```

## 🎯 Supported Conversions on Cloud

| Conversion | Status | Notes |
|------------|--------|-------|
| PDF → DOCX (hybrid) | ✅ Works | Uses PyMuPDF + Groq AI |
| PDF → DOCX (text) | ✅ Works | Uses pdfplumber |
| PDF → DOCX (ocr) | ✅ Works | Needs Tesseract (in packages.txt) |
| DOCX → PDF | ✅ Works | Uses LibreOffice (in packages.txt) |
| CSV → XLSX | ✅ Works | Python only |
| Images → PDF | ✅ Works | Python only |
| Office formats | ✅ Works | Uses LibreOffice (in packages.txt) |

## 🐛 Troubleshooting

### LibreOffice Not Found
If you see "LibreOffice not available" errors:
1. Check `packages.txt` includes all libreoffice packages
2. Wait for full deployment (can take 5+ minutes)
3. Check deployment logs in Streamlit Cloud

### Tesseract Not Found
If OCR mode fails:
1. Ensure `tesseract-ocr` and `tesseract-ocr-eng` in `packages.txt`
2. Redeploy the app

### Groq API Errors
If AI modes fail:
1. Verify GROQ_API_KEY is set in Secrets
2. Check API key is valid
3. Ensure you have Groq API credits

### Memory Issues
If app crashes on large files:
1. Reduce upload size limit in config.toml
2. Use simpler conversion modes (text instead of hybrid)

## 📊 Performance

**Expected Processing Times:**
- PDF → DOCX (text): 1-5 seconds
- PDF → DOCX (hybrid/AI): 10-30 seconds
- DOCX → PDF (LibreOffice): 2-10 seconds
- OCR conversion: 5-20 seconds per page

**Resource Limits:**
- Streamlit Cloud free tier: 1 GB RAM
- Upload size limit: 200 MB (configurable)
- Request timeout: 10 minutes

## 🔒 Security

- Sensitive data warnings disabled in UI (as per requirements)
- Privacy checks still run in background for AI modes
- API keys stored securely in Streamlit Secrets
- Files deleted after conversion

## 📝 Local Testing Before Deploy

Test locally with production settings:
```bash
cd "D:\File Converter"
.\env\Scripts\Activate.ps1
cd FileConverter
streamlit run streamlit_app.py
```

Visit: http://localhost:8501

## ✅ Pre-Deployment Checklist

- [ ] All files committed to Git
- [ ] Repository pushed to GitHub
- [ ] GROQ_API_KEY ready
- [ ] packages.txt includes all system dependencies
- [ ] requirements.txt is up to date
- [ ] App tested locally
- [ ] Main file path: `FileConverter/streamlit_app.py`

## 🎉 Post-Deployment

Once deployed, your app will be available at:
```
https://<your-app-name>.streamlit.app
```

Share this URL with users!
