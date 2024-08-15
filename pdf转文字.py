import os
import traceback
import fitz

def is_white(text):
    """Check if a text span is empty or consists of whitespace."""
    return not text.strip()

class IdentifyHeaders:
    """Compute data for identifying header text."""

    def __init__(self, doc, pages: list = None, body_limit: float = None):
        """Read all text and make a dictionary of fontsizes."""
        if isinstance(doc, fitz.Document):
            mydoc = doc
        else:
            mydoc = fitz.open(doc)

        if pages is None:  # use all pages if omitted
            pages = range(mydoc.page_count)

        fontsizes = {}
        for pno in pages:
            page = mydoc.load_page(pno)
            blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
            for span in [  # look at all non-empty horizontal spans
                s
                for b in blocks
                for l in b["lines"]
                for s in l["spans"]
                if not is_white(s["text"])
            ]:
                fontsz = round(span["size"])
                count = fontsizes.get(fontsz, 0) + len(span["text"].strip())
                fontsizes[fontsz] = count

        if mydoc != doc:
            mydoc.close()

        self.header_id = {}

        if body_limit is None:
            temp = sorted(
                [(k, v) for k, v in fontsizes.items()],
                key=lambda i: i[1],
                reverse=True,
            )
            if temp:
                body_limit = temp[0][0]
            else:
                body_limit = 12

        sizes = sorted([f for f in fontsizes.keys() if f > body_limit], reverse=True)

        for i, size in enumerate(sizes):
            self.header_id[size] = "#" * (i + 1) + " "

    def get_header_id(self, span):
        """Return appropriate markdown header prefix."""
        fontsize = round(span["size"])
        hdr_id = self.header_id.get(fontsize, "")
        return hdr_id

def to_markdown(doc, pages=None, hdr_info=None):
    if isinstance(doc, str):
        doc = fitz.open(doc)

    if not pages:
        pages = range(doc.page_count)

    if not isinstance(hdr_info, IdentifyHeaders):
        hdr_info = IdentifyHeaders(doc)

    page_outputs = []
    textflags = fitz.TEXT_DEHYPHENATE | fitz.TEXT_MEDIABOX_CLIP

    for pno in list(pages):
        page = doc[pno]

        text = page.get_text("text", flags=textflags)

        page_outputs.append(text)

    return page_outputs

def extract_pdf_content(file_path):
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print(f"Could not open {file_path}: {e}")
        return None

    pages = range(doc.page_count)
    md_strings = to_markdown(doc, pages=pages)
    return md_strings

def collect_files(pathname):
    files = []
    for root, _, filenames in os.walk(pathname):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def main(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    files = collect_files(input_dir)

    for path in files:
        if path.lower().endswith(".pdf"):
            try:
                page_contents = extract_pdf_content(path)
                if page_contents is None:
                    continue

                base_filename = os.path.splitext(os.path.basename(path))[0]
                subfolder_path = os.path.join(output_dir, base_filename)
                os.makedirs(subfolder_path, exist_ok=True)

                for page_number, content in enumerate(page_contents, start=1):
                    if len(content) < 500:
                        continue

                    output_filename = f"{base_filename}-page{page_number}.txt"
                    output_path = os.path.join(subfolder_path, output_filename)

                    with open(output_path, "w", encoding="utf8") as f_ou:
                        f_ou.write(content)
                    
            except Exception as e:
                print(f"Error processing {path}: {e}")
                print(traceback.format_exc())

if __name__ == "__main__":
    input_dir = r"/data/zhaoshuofeng/workplace/hongan_data/研报"
    output_dir = r"/data/zhaoshuofeng/workplace/hongan_data/研报/output_texts/all_texts"
    main(input_dir, output_dir)
