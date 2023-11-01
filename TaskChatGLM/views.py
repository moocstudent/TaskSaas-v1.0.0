from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("TaskSaas/chatglm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("TaskSaas/chatglm-6b", trust_remote_code=True).half().cuda()
model = model.eval()
response, history = model.chat(tokenizer, "你好", history=[])
print(response)
response, history = model.chat(tokenizer, "彩票中奖几率计算和彩票号计算", history=history)
print(response)
