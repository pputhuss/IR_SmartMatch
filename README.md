# IR SmartMatch

IR SmartMatch is a web-based resume to company matching tool built for Purdue University career fairs. You upload your resume, pick a major filter, and the system ranks 129 companies by how well they match your background using semantic embeddings. It also shows a skill gap for your top match.

## How to Run

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then run the app:

```bash
python src/app.py
```

Open your browser and go to http://localhost:5000. From there you can upload a PDF resume or paste your resume as plain text, select a major filter, and hit Match to see your results.

The all-MiniLM-L6-v2 model from sentence-transformers will download automatically the first time you run the app. No manual setup needed for that.

## Project Structure

The repo is organized as follows:

- `src/app.py` — Flask backend that handles the API endpoints, resume input, major filtering, and returns ranked results.
- `src/matcher.py` — loads the SentenceTransformer model, generates embeddings for the resume and companies, and computes cosine similarity scores.
- `src/scraper.py` — loads the company data from companies.json and runs keyword detection to auto-tag each company with a major.
- `src/main.py` — entry point for launching the app.
- `frontend/index.html` — the entire frontend, written in HTML/CSS/JS.
- `data/companies.json` — the company dataset with 129 employers from the Purdue Spring 2026 In-Person EXPO, sourced from Career Fair Plus. This file is included in the repo so no download is needed.

## Dependencies

Main packages used:
- flask
- sentence-transformers
- pymupdf
- requests
- scikit-learn

All listed in requirements.txt.

## Code Authorship

All code in this project was written by Prathik Puthussery. No code was copied from external repositories. The external libraries (flask, sentence-transformers, pymupdf, scikit-learn) were used as is without modification.

Claude AI (Anthropic) was used to provide guidance during development and to help write the term paper. All code and implementation decisions are my own.