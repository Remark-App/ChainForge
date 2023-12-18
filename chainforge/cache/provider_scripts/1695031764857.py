from chainforge.providers import provider
import replicate
import os
import time 
import json

REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]

print('==REPLICATE_API_TOKEN=='+REPLICATE_API_TOKEN);

# JSON schemas to pass react-jsonschema-form, one for this provider's settings and one to describe the settings UI.
LLAMA2_SETTINGS_SCHEMA = {
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

models=[
    'replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1', 
    'a16z-infra/llama-2-13b-chat:2a7f981751ec7fdf87b5b91ad4db53683a98082e9ff7bfd12c8cd5ea85980a52',
    'meta/llama-2-7b:527827021d8756c7ab79fde0abbfaac885c37a3ed5fe23c7465093f0878d55ef',
    'mistralai/mixtral-8x7b-instruct-v0.1:2b56576fcfbe32fa0526897d8385dd3fb3d36ba6fd0dbe033c72886b81ade93e',
]

# Our custom model provider for Cohere's text generation API.
@provider(name="LLAMA2",
          emoji="🌈", 
          models=models,
          rate_limit="sequential", # enter "sequential" for blocking; an integer N > 0 means N is the max mumber of requests per minute. 
          settings_schema=LLAMA2_SETTINGS_SCHEMA)
def LLAMA2Completion(prompt: str, model: str, temperature: float = 0.75, **kwargs) -> str:
    print(f"Calling LLAMA2 model {model} with prompt '{prompt}'...")
    # response = co.generate(model=model, prompt=prompt, temperature=temperature, **kwargs)

    print('model==', model)
    true_model = ""

    if(model in models):
        true_model = model
    else:
        true_model = models[0]
        for current_model in models:
            if(current_model.endswith(model)):
                true_model = current_model


    print('true_model=='+true_model)

    machine_types = {
      "CPU": {"public": 0.000100, "private": 0.000200},
      "Nvidia T4 GPU": {"public": 0.000225, "private": 0.000550},
      "Nvidia A40 GPU": {"public": 0.000575, "private": 0.001300},
      "Nvidia A40 (Large) GPU": {"public": 0.000725, "private": 0.001600},
      "Nvidia A100 (40GB) GPU": {"public": 0.001150, "private": 0.002300},
      "Nvidia A100 (80GB) GPU": {"public": 0.001400, "private": 0.003200},
      "8x Nvidia A40 (Large) GPU": {"public": 0.005800, "private": 0.005800},
    }


    start_time = time.perf_counter()

    response = replicate.run(
            true_model,
            input={
                   "prompt": prompt,
            })
    
    response_str =''.join(response)
    end_time = time.perf_counter()
    execution_time = round(end_time - start_time, 3)

    CPU_public = round(machine_types["CPU"]["public"] * execution_time , 6)
    CPU_private = round(machine_types["CPU"]["private"] * execution_time , 6)
    Nvidia_T4_GPU_public = round(machine_types["Nvidia T4 GPU"]["public"] * execution_time , 6)
    Nvidia_T4_GPU_private = round(machine_types["Nvidia T4 GPU"]["private"] * execution_time , 6)
    # 待补全
    Nvidia_A40_GPU_public = round(machine_types["Nvidia A40 GPU"]["public"] * execution_time , 6)
    Nvidia_A40_GPU_private = round(machine_types["Nvidia A40 GPU"]["private"] * execution_time , 6)
    Nvidia_A40_Large_GPU_public = round(machine_types["Nvidia A40 (Large) GPU"]["public"] * execution_time , 6)
    Nvidia_A40_Large_GPU_private = round(machine_types["Nvidia A40 (Large) GPU"]["private"] * execution_time , 6)
    Nvidia_A100_40GB_GPU_public = round(machine_types["Nvidia A100 (40GB) GPU"]["public"] * execution_time , 6)
    Nvidia_A100_40GB_GPU_private = round(machine_types["Nvidia A100 (40GB) GPU"]["private"] * execution_time , 6)
    Nvidia_A100_80GB_GPU_public = round(machine_types["Nvidia A100 (80GB) GPU"]["public"] * execution_time , 6)
    Nvidia_A100_80GB_GPU_private = round(machine_types["Nvidia A100 (80GB) GPU"]["private"] * execution_time , 6)
    Nvidia_8xA40_Large_GPU_public = round(machine_types["8x Nvidia A40 (Large) GPU"]["public"] * execution_time , 6)
    Nvidia_8xA40_Large_GPU_private = round(machine_types["8x Nvidia A40 (Large) GPU"]["private"] * execution_time , 6)



    return json.dumps({'response_str': response_str, 
                       'seconds': execution_time, 
                       'CPU_public': CPU_public, 
                       'CPU_private': CPU_private, 
                       'Nvidia_T4_GPU_public': Nvidia_T4_GPU_public,  
                       'Nvidia_T4_GPU_private': Nvidia_T4_GPU_private,
                       'Nvidia_A40_GPU_public': Nvidia_A40_GPU_public,
                       'Nvidia_A40_GPU_private': Nvidia_A40_GPU_private,
                       'Nvidia_A40_Large_GPU_public': Nvidia_A40_Large_GPU_public,
                       'Nvidia_A40_Large_GPU_private': Nvidia_A40_Large_GPU_private,
                       'Nvidia_A100_40GB_GPU_public': Nvidia_A100_40GB_GPU_public,
                       'Nvidia_A100_40GB_GPU_private': Nvidia_A100_40GB_GPU_private,
                       'Nvidia_A100_80GB_GPU_public': Nvidia_A100_80GB_GPU_public,
                       'Nvidia_A100_80GB_GPU_private': Nvidia_A100_80GB_GPU_private,
                       'Nvidia_8xA40_Large_GPU_public': Nvidia_8xA40_Large_GPU_public,
                       'Nvidia_8xA40_Large_GPU_private': Nvidia_8xA40_Large_GPU_private
                      })