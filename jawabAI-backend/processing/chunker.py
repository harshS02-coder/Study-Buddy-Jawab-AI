from langchain_text_splitters import RecursiveCharacterTextSplitter

#invoice chunking logic
def invoice_chunker(pages: list) -> list[dict]:
    """Chunk invoice with page metadata"""
    sections = []
    keywords = [
        "invoice",
        "bill to",
        "vendor",
        "total",
        "tax",
        "gst",
        "amount",
        "payment"
    ]
    
    for page in pages:
        page_num = page["page_number"]
        text = page["text"]
        lines = text.split("\n")
        buffer = ""

        for line in lines:
            buffer += line + " "
            if any(k in line.lower() for k in keywords):
                sections.append({
                    "text": buffer.strip(),
                    "page": page_num
                })
                buffer = ""

        if buffer.strip():
            sections.append({
                "text": buffer.strip(),
                "page": page_num
            })

    return sections


def chunk_text(pages: list, use_case: str = "study") -> list[dict]:
    """Chunk text while preserving page metadata"""
    print(f"Chunking text for use case: {use_case}")

    if use_case == "invoice":
        chunks = invoice_chunker(pages)
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = []
        for page in pages:
            page_num = page["page_number"]
            text = page["text"]
            split_chunks = splitter.split_text(text)
            
            for chunk in split_chunks:
                chunks.append({
                    "text": chunk,
                    "page": page_num
                })
    
    print(f"Created {len(chunks)} chunks.")
    return chunks
