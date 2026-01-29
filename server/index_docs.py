import os
import shutil
import logging
import sys
import re
import unicodedata
import pickle
import json
import numpy as np
import faiss
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
INPUT_DIR = '../vector_storage/raw_documents'
# If raw_documents doesn't exist in vector_storage, check Documents
ALT_INPUT_DIR = '../vector_storage/Documents'
OUTPUT_DIR = './vector_store'
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

def setup_tesseract():
    try:
        # Set TESSDATA_PREFIX to point to the data folder
        os.environ['TESSDATA_PREFIX'] = r'C:\Users\Dell\anaconda3\envs\venv\Library\share\tessdata'
        
        conda_prefix = sys.prefix
        conda_tesseract = os.path.join(conda_prefix, 'Library', 'bin', 'tesseract.exe')
        
        if os.path.exists(conda_tesseract):
            pytesseract.pytesseract.tesseract_cmd = conda_tesseract
            logger.info(f"🔍 Found Conda Tesseract at: {conda_tesseract}")
        elif os.name == 'nt':
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                os.path.join(os.getenv('LOCALAPPDATA', ''), r'Tesseract-OCR\tesseract.exe')
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    logger.info(f"🔍 Found System Tesseract at: {p}")
                    break
        
        version = pytesseract.get_tesseract_version()
        logger.info(f"✅ Tesseract OCR Version: {version}")
    except Exception as e:
        logger.error(f"❌ Tesseract OCR setup failed: {e}")
        sys.exit(1)

def normalize_text(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'page \d+ of \d+', '', text)
    text = re.sub(r'page \d+', '', text)
    return text

def run_indexing():
    # 1. Setup environment
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    setup_tesseract()
    
    # 2. Find files
    current_input_dir = INPUT_DIR
    if not os.path.exists(current_input_dir):
        current_input_dir = ALT_INPUT_DIR
        
    if not os.path.exists(current_input_dir):
        logger.warning(f"⚠️ Input directory {INPUT_DIR} not found. Creating it.")
        os.makedirs(current_input_dir)
        logger.info(f"Please place documents in {os.path.abspath(current_input_dir)} and run again.")
        return

    source_files = [os.path.join(current_input_dir, f) for f in os.listdir(current_input_dir) 
                   if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png'))]
    
    if not source_files:
        logger.warning(f"No documents found in {current_input_dir}")
        return

    logger.info(f"Processing {len(source_files)} documents...")

    # 3. OCR Extraction
    documents = []
    for doc_idx, filename in enumerate(source_files):
        logger.info(f"📄 Processing {filename} ({doc_idx+1}/{len(source_files)})...")
        full_text = ""
        file_ext = filename.split('.')[-1].lower()
        
        try:
            if file_ext == 'pdf':
                poppler_bin = r'C:\Users\Dell\anaconda3\envs\venv\Library\bin'
                images = convert_from_path(filename, poppler_path=poppler_bin)
                for image in images:
                    full_text += pytesseract.image_to_string(image) + "\n"
            else:
                full_text += pytesseract.image_to_string(Image.open(filename))
            
            documents.append({"doc_id": doc_idx, "source": filename, "raw_text": full_text})
            logger.info(f"   ✅ Extracted {len(full_text)} characters.")
        except Exception as e:
            logger.error(f"   ❌ Error processing {filename}: {e}")

    # 4. Cleaning & Chunking
    chunks = []
    chunk_counter = 0
    for doc in documents:
        clean_text = normalize_text(doc['raw_text'])
        for i in range(0, len(clean_text), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk_text = clean_text[i : i + CHUNK_SIZE]
            if len(chunk_text) < 50: continue
            
            chunks.append({
                "chunk_id": chunk_counter,
                "doc_id": doc['doc_id'],
                "text": chunk_text,
                "source": os.path.basename(doc['source']),
                "position": i
            })
            chunk_counter += 1

    logger.info(f"✅ Generated {len(chunks)} chunks.")

    # 5. Embeddings
    logger.info(f"Loading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    texts = [c['text'] for c in chunks]
    logger.info(f"Encoding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype(np.float32)

    # 6. Build FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    logger.info(f"✅ FAISS Index created. Total vectors: {index.ntotal}")

    # 7. Metadata Store
    metadata_store = {}
    text_store = {}
    for i, chunk in enumerate(chunks):
        c_id = chunk['chunk_id']
        metadata_store[c_id] = { 
            "doc_id": chunk['doc_id'], 
            "source": chunk['source'], 
            "position": chunk['position'] 
        }
        text_store[c_id] = chunk['text']

    # 8. Save
    index_path = os.path.join(OUTPUT_DIR, 'index.faiss')
    metadata_path = os.path.join(OUTPUT_DIR, 'metadata.pkl')
    texts_path = os.path.join(OUTPUT_DIR, 'texts.pkl')

    faiss.write_index(index, index_path)
    with open(metadata_path, 'wb') as f: pickle.dump(metadata_store, f)
    with open(texts_path, 'wb') as f: pickle.dump(text_store, f)
    
    logger.info(f"✅ All artifacts saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_indexing()
