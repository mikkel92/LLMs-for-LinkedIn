import pandas as pd
import json
from tqdm import tqdm

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

from peft import PeftModel
from huggingface_hub import login
import torch
from mikkel_secrets import secrets


def load_model_and_tokenizer():

    login(secrets["llama"]["token"])
    model_id = "meta-llama/Llama-2-7b-chat-hf"

    compute_dtype = getattr(torch, "float16")

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=False,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"


    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        #torch_dtype=torch.bfloat16, 
        quantization_config=quant_config,
        device_map={"": 0},
    )

    model.config.use_cache = False
    model.config.pretraining_tp = 1

    return model, tokenizer



df = pd.read_csv("linkedin_posts.csv", index_col=0)
model, tokenizer = load_model_and_tokenizer()

device = "cuda:0" if torch.cuda.is_available() else "cpu"

print("Summarising texts, this might take a while...")

with open("processed_posts.jsonl", "w") as f:
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):

        init_prompt = f"Create a LinkedIn post of about {round(len(row['texts']), -2)} characters using the language and tone of Mikkel Jensen. "
        to_sum = """
            Write a concise description and summary of the following text delimited by triple backquotes. 
            It should have a length of 100 tokens maximum, but be as short as possible while adequately describing the content.
            It should contain a description of the post, how it's built up and how many points were made.
            Start the summary like this: "The post summary is:"
            ```""" + row["texts"] + """```"""
        inputs = tokenizer(to_sum, return_tensors="pt").to(device)

        outputs = model.generate(**inputs)
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True).split("```")[-1]

        save_dict = {'prompt': str(init_prompt + summary), 'completion': row["texts"]}

        json.dump(save_dict, f)
        f.write("\n")
