import os
import re
import openai
import time

# ------------------ CONFIG ------------------
SOURCE_FOLDER = "input"       # folder containing .srt/.txt files
OUTPUT_FOLDER = "output"      # folder for translated files
TARGET_LANGUAGE = "Polish"    # choose the target language
MODEL = "gpt-5-mini"          # choose a model
CHUNK_SIZE = 2000             # characters per chunk (approx, for multiple blocks)

PROMPT = f"You are a translator for an API. Translate into {TARGET_LANGUAGE}. Only translate the subtitle text lines, never the index numbers or timestamps. Keep the same number of blocks and the same line breaks, also keep the same exact order of the strings in a response. Respond with plain text only, block by block. Make it sound natural in {TARGET_LANGUAGE}."
# --------------------------------------------

openai.api_key = "YOUR OPENAI API KEY HERE" # Paste your OpenAi Api key to this string


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def parse_srt_blocks(text):
    """
    Returns a list of dicts:
    [{"index": str, "timestamp": str, "lines": [list of text lines]}, ...]
    """
    blocks = text.strip().split("\n\n")
    parsed = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) >= 3:
            parsed.append({
                "index": lines[0],
                "timestamp": lines[1],
                "lines": lines[2:]
            })
        elif len(lines) >= 2:
            parsed.append({
                "index": lines[0],
                "timestamp": lines[1],
                "lines": []
            })
        elif lines:
            parsed.append({
                "index": lines[0],
                "timestamp": "",
                "lines": []
            })
    return parsed


def reconstruct_srt(blocks):
    """
    Rebuilds srt text from parsed blocks (with translated lines).
    """
    output_blocks = []
    for block in blocks:
        entry = [block["index"], block["timestamp"]] + block["lines"]
        output_blocks.append("\n".join(entry))
    return "\n\n".join(output_blocks)


def split_blocks_into_chunks(blocks, chunk_size=CHUNK_SIZE):
    """
    Splits blocks into chunks without breaking a block.
    """
    chunks = []
    current_chunk = []
    current_len = 0

    for block in blocks:
        block_len = sum(len(line) for line in block["lines"]) + len(block["lines"])
        if current_len + block_len > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_len = 0
        current_chunk.append(block)
        current_len += block_len

    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def translate_chunk(chunk, max_retries=3, delay=30):
    """
    Translate only subtitle text lines, keeping structure intact.
    """
    # Prepare text to send: only the lines, joined by newlines, separated by block markers
    text_to_translate = ""
    for i, block in enumerate(chunk):
        text_to_translate += f"### BLOCK {i+1} ###\n"
        text_to_translate += "\n".join(block["lines"]) if block["lines"] else ""
        text_to_translate += "\n\n"

    for attempt in range(1, max_retries + 1):
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": text_to_translate.strip()}
                ]
            )
            translated_text = response.choices[0].message.content.strip()

            # Split back into blocks
            translated_blocks = translated_text.split("### BLOCK ")
            results = []
            for i, raw in enumerate(translated_blocks):
                if not raw.strip():
                    continue
                # remove "n ###" marker
                raw = re.sub(r"^\d+\s*###", "", raw).strip()
                lines = raw.splitlines()
                results.append(lines)

            # align results with input blocks
            for block, trans_lines in zip(chunk, results):
                block["lines"] = trans_lines

            return chunk

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached, returning original chunk.")
                return chunk


def translate_file(input_path, output_path):
    text = read_file(input_path)
    blocks = parse_srt_blocks(text)
    chunks = split_blocks_into_chunks(blocks)

    translated_blocks = []
    for i, chunk in enumerate(chunks, 1):
        print(f"Translating chunk {i}/{len(chunks)} of {os.path.basename(input_path)}...")
        translated_chunk = translate_chunk(chunk)
        translated_blocks.extend(translated_chunk)

    full_translation = reconstruct_srt(translated_blocks)
    write_file(output_path, full_translation)
    print(f"Saved translation to {output_path}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, SOURCE_FOLDER)
    output_dir = os.path.join(base_dir, OUTPUT_FOLDER)

    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(source_dir):
        if file_name.lower().endswith((".srt", ".txt")):
            input_path = os.path.join(source_dir, file_name)
            output_path = os.path.join(output_dir, file_name)

            translate_file(input_path, output_path)


if __name__ == "__main__":
    main()
