from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import os


MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models/t5-base-finetuned-summarize-news")


tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
model.eval()

def summarize_text(text: str, max_len: int = 150) -> str:
    """
    Summarize input text using t5-base-finetuned-summarize-news model.

    Args:
        text (str): Input text to summarize.
        max_len (int): Maximum length of generated summary.

    Returns:
        str: Generated summary string.
    """
   
    input_text = "summarize: " + text.strip()
    inputs = tokenizer(
        input_text,
        max_length=512,
        truncation=True,
        padding="longest",
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=max_len,
            num_beams=5,
            length_penalty=2.0,
            early_stopping=True,
            no_repeat_ngram_size=3
        )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary


if __name__ == "__main__":
    sample_text = (
        "The South of France is known for its enchanting coastline, delicious cuisine, "
        "and rich cultural history. Visitors can enjoy beaches, museums, markets, and festivals."
    )
    print("Original Text:\n", sample_text)
    print("\nGenerated Summary:\n", summarize_text(sample_text))
