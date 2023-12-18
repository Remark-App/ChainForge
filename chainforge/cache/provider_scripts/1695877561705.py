from chainforge.providers import provider
import requests
import os
import time 
import json


DEEPINFRA_API_TOKEN = os.environ["DEEPINFRA_API_TOKEN"]

print('==REPLICATE_API_TOKEN==', DEEPINFRA_API_TOKEN);

# JSON schemas to pass react-jsonschema-form, one for this provider's settings and one to describe the settings UI.
DEEPINFRA_SETTINGS_SCHEMA = {
  "settings": {
    "temperature": {
        "type": "number",
        "title": "temperature",
        "description": "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.",
        "default": 1,
        "minimum": 0,
        "maximum": 2,
        "multipleOf": 0.01
    },
    "max_tokens": {
        "type": "integer",
        "title": "max_tokens",
        "description": "The maximum number of tokens to generate in the chat completion. (The total length of input tokens and generated tokens is limited by the model's context length.)"
    },
  },
  "ui": {
    "temperature": {
      "ui:help": "Defaults to 1.0.",
      "ui:widget": "range"
    },
    "max_tokens": {
      "ui:help": "Defaults to infinity."
    },
  }
}

DEEPINFRAmodels=[
    'meta-llama/Llama-2-13b-chat-hf', 
    'meta-llama/Llama-2-70b-chat-hf',
]

# Our custom model provider for Cohere's text generation API.
@provider(name="DEEPINFRA",
          emoji="🚀", 
          models=DEEPINFRAmodels,
          rate_limit="sequential", # enter "sequential" for blocking; an integer N > 0 means N is the max mumber of requests per minute. 
          settings_schema=DEEPINFRA_SETTINGS_SCHEMA)
def DEEPINFRACompletion(prompt: str, model: str, temperature: float = 0.75, **kwargs) -> str:
    print(f"Calling DEEPINFRA model {model} with prompt '{prompt}'...")
    # response = co.generate(model=model, prompt=prompt, temperature=temperature, **kwargs)
    print('model==', model)
    true_model = ""

    if(model in DEEPINFRAmodels):
        true_model = model
    else:
        true_model = DEEPINFRAmodels[0]
        for current_model in DEEPINFRAmodels:
            if(current_model.endswith(model)):
                true_model = current_model


    print('true_model==', true_model)


    start_time = time.perf_counter()

    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEEPINFRA_API_TOKEN}',
    }


    input_params = '[INST] ' + prompt +' [/INST] '
    # 设置请求体
    data = {
        'input': input_params,
    }

    url = 'https://api.deepinfra.com/v1/inference/'+ true_model

    print('==url', url)

    response = requests.post(url, headers=headers, json=data)

    response_json = response.json()


    # 检查状态是否为'succeeded'
    if response_json['inference_status']['status'] == 'succeeded':
        # 获取生成的文本
        generated_text = response_json['results'][0]['generated_text']
        # 移除指令标记
        pure_generated_text = generated_text.replace(input_params, '')
        # 添加到结果中
        response_json['results'][0]['pure_generated_text'] = pure_generated_text
        # print(response_json)
    else:
        print('Inference failed')

    # 打印响应内容
    print(response_json)

    end_time = time.perf_counter()
    execution_time = round(end_time - start_time, 3)

    return json.dumps({'response_str': response_json['results'][0]['pure_generated_text'], 
                       'seconds': execution_time,
                       'response_json': response_json,
                      })