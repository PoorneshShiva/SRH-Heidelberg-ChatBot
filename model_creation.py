import torch
from transformers import BitsAndBytesConfig

import os

from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.core import ServiceContext
from llama_index.embeddings.langchain import LangchainEmbedding

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms.huggingface import HuggingFaceLLM


def messages_to_prompt(messages):
    prompt = ""
    for message in messages:
        if message.role == 'system':
            prompt += f"<|system|>\n{message.content}</s>\n"
        elif message.role == 'user':
            prompt += f"<|user|>\n{message.content}</s>\n"
        elif message.role == 'assistant':
            prompt += f"<|assistant|>\n{message.content}</s>\n"

    # ensure we start with a system prompt, insert blank if needed
    if not prompt.startswith("<|system|>\n"):
        prompt = "<|system|>\n</s>\n" + prompt

    # add final assistant prompt
    prompt = prompt + "<|assistant|>\n"

    return prompt


def completion_to_prompt(completion):
    return f"<|system|>I am a user who's looking for information. You don't know anything about me.\n</s>\n<|user|>\n{completion}</s>\n<|assistant|>\n"


# quantize to save memory
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    # bnb_4bit_use_double_quant=True
    llm_int8_enable_fp32_cpu_offload=True
)

llm = HuggingFaceLLM(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    tokenizer_name="meta-llama/Llama-2-7b-chat-hf",
    context_window=3900,
    max_new_tokens=256,
    model_kwargs={"quantization_config": quantization_config},
    generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    device_map="auto"
)

embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"))

try:
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_file_directory, 'srh_index')
    print("Directory of the current file:", folder_path)
except:
    folder_path = 'srh_index'
# quantizer = bnb.GemmQuantizer(act_bits=8, weight_bits=8)
from llama_index.core.indices.loading import load_index_from_storage, StorageContext

# Specify the directory where you want to store the index
storage_dir = folder_path

# Create a StorageContext instance
storage_context = StorageContext.from_defaults(persist_dir=storage_dir)

# # Persist the index to disk
# storage_context.persist(storage_dir)


embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"))
service_context = ServiceContext.from_defaults(
    chunk_size=1024,
    llm=llm,
    embed_model=embed_model
)

documents = SimpleDirectoryReader("./new_data").load_data()

index = VectorStoreIndex.from_documents(documents, service_context=service_context)
query_engine = index.as_query_engine()
index.storage_context.persist("srh")
