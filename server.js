const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');

const PORT = 0xDEAD;

const app = express();

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, 'uploads'));
  },
  filename: (req, file, cb) => {
    const timestamp = Date.now();
    const sanitized = file.originalname.replace(/\s+/g, '_');
    const uniqueName = `${timestamp}_${sanitized}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ storage });

app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }
  res.json({ filename: req.file.filename });
});

app.get('/chapters/:filename', (req, res) => {
  const filename = req.params.filename;
  const filepath = path.join(__dirname, 'uploads', filename);

  const pythonPath = path.join(__dirname, 'venv', 'bin', 'python');
  execFile(pythonPath, ['parser.py', filepath], { maxBuffer: 24 * 1024 * 1024}, (error, stdout, stderr) => {
    // 24 MiB because we're just dumping to stdout instead of TCP, but need TCP server later because this is straight up dumb
    if (error) {
      console.error('Python error:', error);
      return res.status(500).json({ error: 'Failed to extract chapters.' });
    }

    try {
      const json = JSON.parse(stdout);
      res.json(json);
    } catch (parseErr) {
      console.error('JSON parse error:', parseErr);
      res.status(500).json({ error: 'Invalid JSON returned by parser.' });
    }
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port: ${PORT}`);
});
