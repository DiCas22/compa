# Compa

Compa is a CLI tool to losslessly compress text‑heavy files (PDF, TXT, HTML, code) into Zstandard (`.zst`) archives, tag them with human‑readable topics, and provide quick access (compress, list, search, open, decompress).

## Goals

- Efficient, lossless compression via Zstandard (level 19 by default)
- Optional PDF optimization using Ghostscript `/ebook`
- Topic-based tagging for fast retrieval
- One‑shot `open` that auto‑cleans temporary files
- Future: seekable archives for random access, SQLite-backed tag index, minimal GUI

## Installation

```bash
git clone https://github.com/<your‑user>/compa.git
cd compa
python3 -m venv venv
source venv/bin/activate
pip install -e .

# system dependencies (Debian/Ubuntu)
sudo apt install zstd ghostscript poppler-utils
```

## Usage

### compress
```bash
compa compress <file> [--topics TAG1,TAG2] [--level N] [--threads N] [--no-pdf-opt]
```
- `<file>`: path to a file (PDF, TXT, etc.)
- `--topics`: comma-separated tags (e.g. `AI,Robotics`)
- `--level`: Zstd compression level (default 19)
- `--threads`: number of worker threads (0=auto)
- `--no-pdf-opt`: skip Ghostscript PDF optimization

### list
```bash
compa list <topic1,topic2,...>
```
Lists all archives tagged with **all** specified topics.

### search
```bash
compa search "<phrase>" [--context N]
```
Searches all compressed archives for `<phrase>` and prints matches with context:
- Decompresses on-the-fly (text files) or uses `pdftotext` for PDF archives.
- `--context`, `-c`: number of characters around each match (default 50)

Example:
```bash
compa search "Better sleep" -c 40
# Output:
# book.pdf.zst: "Better sleep is achieved through less noisy ambient..."
# notes.txt.zst: "You can get a better sleep if you reduce screen time..."
```

### open
```bash
compa open <archive.zst> [--keep-temp] [--wait SECONDS]
```
- Decompresses to a temp directory and opens with the default viewer
- Deletes the temp copy on ENTER or after `--wait` seconds
- `--keep-temp` preserves the decompressed file

### decompress
```bash
compa decompress <archive.zst> [--out DIR]
```
Restores the original file into `DIR` (default: current directory).

## Project Layout

```
compa/
├── compa/            # Python package
│   ├── cli.py
│   ├── compress.py
│   ├── index_ini.py
│   ├── utils.py
│   └── search.py
├── files/            # all .zst archives
├── pyproject.toml
└── README_template.txt
```

## Publishing to GitHub

1. **Add or verify the remote**  
   ```bash
   git remote add origin https://github.com/<your‑user>/compa.git
   git branch -M main
   git push -u origin main
   ```

## Contributing

1. Fork & clone this repository  
2. Create & activate venv  
3. `pip install -e .`  
4. Create a branch: `git checkout -b feat/my-feature`  
5. Make changes, commit `git commit -m "Description"`  
6. Push & open a Pull Request  

## License

MIT License — see LICENSE for details.