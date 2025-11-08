# 🎵 AI Stem Separator - Complete Setup Guide

## Overview

This guide shows you how to build a functional AI stem separator that can extract vocals, drums, bass, and other instruments from audio files.

## 🚀 Quick Start Options

### Option 1: Simple Python Script (Easiest)
Best for: Local processing, command-line usage

### Option 2: FastAPI Web Server (Recommended)
Best for: Web apps, API integration, multiple users

### Option 3: React Web App (Full Stack)
Best for: Complete web application with UI

---

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Demucs (state-of-the-art stem separation)
pip install demucs

# For API server (Option 2)
pip install fastapi uvicorn python-multipart

# For audio processing
pip install torch torchaudio
```

### Step 2: Test Installation

```bash
# Test demucs installation
python -m demucs --help

# Download a test model
python -m demucs -n htdemucs --help
```

---

## 🎯 Implementation Options

### Option 1: Simple Script

```python
# stem_separator_simple.py
import subprocess
import sys

def separate_audio(input_file, output_dir="output"):
    """Separate audio into 4 stems: vocals, drums, bass, other"""
    cmd = [
        "python", "-m", "demucs",
        "-n", "htdemucs",  # Model name
        "-o", output_dir,   # Output directory
        input_file
    ]
    
    print(f"Separating {input_file}...")
    subprocess.run(cmd, check=True)
    print(f"Done! Check {output_dir} folder")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stem_separator_simple.py <audio_file>")
        sys.exit(1)
    
    separate_audio(sys.argv[1])
```

**Usage:**
```bash
python stem_separator_simple.py song.mp3
```

### Option 2: Web API Server

Use the `stem_separator_api.py` file provided.

**Run the server:**
```bash
uvicorn stem_separator_api:app --reload --host 0.0.0.0 --port 8000
```

**Test the API:**
```bash
# Upload file
curl -X POST http://localhost:8000/api/separate \
  -F "file=@song.mp3" \
  -F "model=htdemucs"

# Check status
curl http://localhost:8000/api/status/{job_id}

# Download stems
curl http://localhost:8000/api/download/{job_id}/vocals -o vocals.wav
```

### Option 3: React Frontend

1. Use the `StemSeparator.jsx` component provided
2. Install dependencies:

```bash
npm install lucide-react
```

3. Add to your React app:

```jsx
import StemSeparator from './StemSeparator';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <StemSeparator />
    </div>
  );
}
```

---

## 🎨 Available Models

| Model | Quality | Speed | Best For |
|-------|---------|-------|----------|
| `htdemucs` | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Recommended for most uses |
| `htdemucs_ft` | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Fine-tuned version |
| `mdx_extra` | ⭐⭐⭐⭐⭐⭐ | ⚡⚡ | Best quality (slower) |
| `mdx_extra_q` | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | Fast processing |

---

## 🔧 Advanced Features

### 1. Separate Only Vocals

```python
cmd = [
    "python", "-m", "demucs",
    "--two-stems=vocals",  # Only vocals + instrumental
    "-n", "htdemucs",
    "song.mp3"
]
```

### 2. Use GPU Acceleration

```python
# Automatically uses GPU if available
# Check with:
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

### 3. Batch Processing

```python
import os
from pathlib import Path

def batch_separate(input_dir, output_dir="output"):
    audio_files = list(Path(input_dir).glob("*.mp3"))
    audio_files.extend(Path(input_dir).glob("*.wav"))
    
    for audio_file in audio_files:
        print(f"\nProcessing: {audio_file.name}")
        cmd = ["python", "-m", "demucs", "-n", "htdemucs", 
               "-o", output_dir, str(audio_file)]
        subprocess.run(cmd)
```

### 4. Custom Model Settings

```python
# High quality, slower
cmd = ["python", "-m", "demucs", 
       "-n", "mdx_extra",
       "--segment", "10",  # Segment length (lower = more memory efficient)
       "--overlap", "0.25",  # Overlap between segments
       "song.mp3"]

# Fast processing
cmd = ["python", "-m", "demucs",
       "-n", "mdx_extra_q",
       "--int24",  # Use int24 for faster processing
       "song.mp3"]
```

---

## 📊 Performance Tips

### 1. GPU Acceleration
- **10-50x faster** than CPU
- Requires: NVIDIA GPU + CUDA toolkit
- Install: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

### 2. Memory Management
```python
# For large files, use segments
cmd = ["python", "-m", "demucs", 
       "--segment", "10",  # Process in 10-second chunks
       "large_song.mp3"]
```

### 3. Multi-file Processing
```python
# Process multiple files at once
cmd = ["python", "-m", "demucs", "-n", "htdemucs", 
       "song1.mp3", "song2.mp3", "song3.mp3"]
```

---

## 🌐 Deploy to Production

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install demucs fastapi uvicorn python-multipart torch torchaudio

# Copy API code
COPY stem_separator_api.py .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "stem_separator_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t stem-separator .
docker run -p 8000:8000 stem-separator
```

### Using Cloud Services

**AWS Lambda:**
- Package as Lambda layer
- Use SageMaker for large files
- Store outputs in S3

**Google Cloud Run:**
- Deploy Docker container
- Auto-scaling
- Pay per use

**Vercel/Netlify:**
- Deploy React frontend
- Use separate API server for processing

---

## 🎯 Integration Examples

### For AISim App

```jsx
// Add to your tools section
const StemSeparatorTool = () => {
  return (
    <div className="tool-card">
      <Music className="tool-icon" />
      <h3>Stem Separator</h3>
      <p>Extract vocals, drums, bass from any song</p>
      <StemSeparator />
    </div>
  );
};
```

### For Mobile App

```javascript
// React Native
import DocumentPicker from 'react-native-document-picker';

const uploadAndSeparate = async () => {
  const file = await DocumentPicker.pick({
    type: [DocumentPicker.types.audio],
  });
  
  const formData = new FormData();
  formData.append('file', {
    uri: file.uri,
    type: file.type,
    name: file.name,
  });
  
  const response = await fetch('https://api.yourdomain.com/api/separate', {
    method: 'POST',
    body: formData,
  });
};
```

---

## 🐛 Troubleshooting

### Issue: "RuntimeError: CUDA out of memory"
**Solution:** Use smaller segments
```python
cmd = ["python", "-m", "demucs", "--segment", "5", "song.mp3"]
```

### Issue: "Model not found"
**Solution:** Models download automatically on first use. Check internet connection.

### Issue: Slow processing
**Solution:** 
1. Use GPU if available
2. Use quantized model (`mdx_extra_q`)
3. Reduce segment overlap

### Issue: Poor quality separation
**Solution:**
1. Use `mdx_extra` model
2. Ensure input file is high quality
3. Try different models for different music types

---

## 📈 Comparison with Alternatives

| Tool | Quality | Speed | License | Cost |
|------|---------|-------|---------|------|
| **Demucs** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ | MIT | Free |
| Spleeter | ⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ | MIT | Free |
| iZotope RX | ⭐⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Commercial | $$$$ |
| Lalal.ai | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ | API | $$ |

---

## 🎓 How It Works

1. **Hybrid Spectrogram**: Converts audio to frequency domain
2. **Deep Learning**: U-Net architecture separates sources
3. **Transformer**: Captures long-term dependencies
4. **Reconstruction**: Converts back to audio

**Model Architecture:**
- Encoder: Extracts features from audio
- Transformer: Models relationships between frequencies
- Decoder: Reconstructs individual stems

---

## 📚 Additional Resources

- **Demucs GitHub**: https://github.com/facebookresearch/demucs
- **Paper**: "Hybrid Spectrogram and Waveform Source Separation"
- **Demos**: https://ai.honu.io/red=demucs/
- **Discord**: Demucs community support

---

## 🎉 Next Steps

1. ✅ Install dependencies
2. ✅ Test with a simple script
3. ✅ Set up API server (optional)
4. ✅ Build frontend interface
5. ✅ Deploy to production
6. ✅ Integrate into your app

**Your stem separator is ready to use! 🎵**
