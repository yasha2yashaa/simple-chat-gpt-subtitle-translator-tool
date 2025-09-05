# Simple ChatGPT Subtitle Translator

This repository contains a simple Python script I made for **translating subtitles (`.srt` and `.txt` files)** into any target language using the OpenAI API, since I couldn't find any myself. 
The script preserves subtitle structure, timestamps, and block numbering while translating only the spoken text lines. For the script to work its required to paste your own OpenAI API key into the script, and changing the target language to the desired one - more details below.

---

## ✨ Features
- Translates `.srt` or plain `.txt` subtitle files into a target language.
- Preserves subtitle block structure, indexes, and timestamps.
- Splits large subtitle files into manageable chunks before sending to the API.
- Handles retries with backoff in case of API errors.
- Outputs translated files into a dedicated folder.

---

## 📂 Repository Structure
```

.
├── input/          # Place your original .srt/.txt files here
├── output/         # Translated files will appear here
├── main.py         # Main translation script
└── README.md

````

---

## ⚙️ Requirements

- Python 3.8+
- OpenAI Python package

Install dependencies:
```bash
pip install openai
````

---

## 🔑 Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. Open the script (`main.py`) with text editor and paste your OpenAI API key:

   ```python
   openai.api_key = "YOUR OPENAI API KEY HERE"
   ```

3. Adjust configuration at the top of the script if needed:

   ```python
   SOURCE_FOLDER = "input"         # Where subtitle files are placed, no need to change it
   OUTPUT_FOLDER = "output"        # Where translations are saved, no need to change it
   TARGET_LANGUAGE = "Polish"      # Change target language to the desired one
   MODEL = "gpt-5-mini"            # Model to use, no need to change it
   CHUNK_SIZE = 2000               # Approx. characters to translate per chunk, no need to change it
   ```

---

## ▶️ Usage

1. Place your subtitle files (`.srt` or `.txt`) in the `input/` folder.
   Example:

   ```
   input/
   ├── movie1.srt
   └── episode1.srt
   ```

2. Run the script:

   ```bash
   python main.py
   ```

3. Translated files will be saved into the `output/` folder, with the same filenames:

   ```
   output/
   ├── movie1.srt
   └── episode1.srt
   ```

---

## 📝 Notes

* The script translates only the subtitle text lines, never timestamps or block numbers.
* The translation prompt is designed to keep subtitles natural while preserving timing and structure.
* If a file is too large, it will be automatically split into multiple chunks for translation.
* Retries are handled with exponential backoff in case of network/API issues.

---

## 🚀 Example

**Input (`input/example.srt`):**

```
1
00:00:01,000 --> 00:00:03,000
Hello, how are you?

2
00:00:04,000 --> 00:00:06,000
I'm fine, thank you!
```

**Output (`output/example.srt` after translating into Polish):**

```
1
00:00:01,000 --> 00:00:03,000
Cześć, jak się masz?

2
00:00:04,000 --> 00:00:06,000
W porządku, dziękuję!
```

---

## 📜 License

This project is licensed under the MIT License – feel free to use, modify, and share.

---

