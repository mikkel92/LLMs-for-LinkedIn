## Fine-tuning LLM for writing LinkedIn posts in Your own language

The notebook in this Repo is an example of how to fine-tune Facebooks Llama-2-7b model, to write LinkedIn posts in Your own language.
I have included some of my own LinkedIn posts for the training data. Replace these with Your own data to personalize the experience!


The code was run using a single Nvidia RTX4090 containing 24GB of VRAM. I believe the code can be tweaked to run on a GPU with 16GB VRAM if necessary.
It can also be run on a CPU although it will take much longer!

Make sure to install a cuda enabled version of PyTorch first, if You want to run this code with a GPU.
