# from transformers import AutoModelForCausalLM, AutoTokenizer

# model_name = "/Users/chenshuai18/.cache/modelscope/hub/models/Qwen/Qwen3___5-0___8B" # 本地模型路径

# model = AutoModelForCausalLM.from_pretrained(
#     model_name,
#     dtype="auto",
#     device_map="auto"
# )
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# prompt = "Hello!"
# messages = [
#     {"role": "user", "content": prompt}
# ]
# text = tokenizer.apply_chat_template(
#     messages,
#     tokenize=False,
#     add_generation_prompt=True,
#     enable_thinking=False
# )
# model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# generated_ids = model.generate(
#     **model_inputs,
#     max_new_tokens=512,
#     top_k=20,
#     top_p=1.00, 
#     temperature= 1.0, 
#     do_sample= True, 
#     repetition_penalty= 1.0
# )
# generated_ids = [
#     output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
# ]

# response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
# print(response)

from modelscope import AutoModelForCausalLM, AutoTokenizer

# model_name = "Qwen/Qwen2.5-0.5B-Instruct"
model_name = "/Users/chenshuai18/.cache/modelscope/hub/models/Qwen/Qwen3___5-0___8B" # 本地模型路径


model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prompt = "Give me a short introduction to large language model."
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)