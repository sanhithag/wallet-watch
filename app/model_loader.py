import os, logging
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
try:
    from transformers import BitsAndBytesConfig
    import bitsandbytes as bnb
except Exception:
    BitsAndBytesConfig = None
import torch

MODEL_REPO = os.environ.get('LOCAL_MODEL_PATH', 'ibm-granite/granite-3.3-2b-instruct')
ENABLE_4BIT = os.environ.get('ENABLE_4BIT', '1') == '1'

def load_pipeline():
    # Try to load pipeline with optional 4-bit quantization if supported
    try:
        if ENABLE_4BIT and BitsAndBytesConfig is not None:
            bnb_config = BitsAndBytesConfig(load_in_4bit=True,
                                            bnb_4bit_compute_dtype=torch.float16,
                                            bnb_4bit_use_double_quant=True,
                                            bnb_4bit_quant_type='nf4')
            pipe = pipeline('text-generation', model=MODEL_REPO, device_map='auto', quantization_config=bnb_config)
            return pipe, '4bit'
        else:
            # fallback to normal pipeline
            pipe = pipeline('text-generation', model=MODEL_REPO, device_map='auto')
            return pipe, 'fp'
    except Exception as e:
        logging.error(f'Pipeline load failed: {e}')
        # attempt a lightweight tokenizer-only check
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO)
            return None, 'tokenizer-only'
        except Exception as e2:
            return None, 'failed'
