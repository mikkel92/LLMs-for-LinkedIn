# Fine-tuning LLM for writing LinkedIn posts in Your own language

The scripts in this repo enables scraping your own LinkedIn posts, analysing them, creating a dataset for fine-tuning and a notebook showcasing how to fine-tune Facebooks Llama-2-7b model, to write LinkedIn posts in Your own tone.

I'm using Llama-2 here. Feel free to change it to a model of your liking.

I have included some of my own LinkedIn posts for the training data. Replace these with Your own data to personalize the experience!


The code was run using a single Nvidia RTX4090 containing 24GB of VRAM. I believe the code can be tweaked to run on a GPU with 16GB VRAM if necessary.
It can also be run on a CPU although it will take much longer!

Make sure to install a cuda enabled version of PyTorch first, if You want to run this code with a GPU.

# Usage
Start by editing the script "scrape_linkedin_posts.py". 
Fill out your login detals in the script, as it requires your LinkedIn credentials. There's also an option to specify your chrome profile folder, to load saved LinkedIn credentials from there.

By default my posts are scraped. Change to your own profile link.

Running "scrape_linkedin_posts.py" will then save a file called "linkedin_posts.csv".

Use the notebook "analyse_posts.ipynb" to start a simple analysis of post statistics.

"process_linkedin_posts.py" will create a new file using the data in "linkedin_posts.csv". The new file is formatted for fine-tuning Llama-2 and is called "processed_posts.jsonl".

Run the notebook "finetune_llama_to_linkedin.ipynb" to create and use a fine-tuned version of Llama-2.
