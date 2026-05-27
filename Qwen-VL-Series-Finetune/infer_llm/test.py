import requests
from openai import OpenAI
import json

def test_with_openai_client():
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )
    
    response = client.chat.completions.create(
        model="/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/outputmodel/omniearth",
        messages=[
            {"role": "user", "content": "hello"}
        ],
        max_tokens=10
    )
    
    print("Response Content:", response.choices[0].message.content)
    print("Full Response:")
    print(json.dumps({
        "id": response.id,
        "model": response.model,
        "choices": [{
            "message": {
                "role": response.choices[0].message.role,
                "content": response.choices[0].message.content
            },
            "finish_reason": response.choices[0].finish_reason
        }],
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
    }, indent=2, ensure_ascii=False))
    
    return response

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("方式2: 使用 OpenAI 客户端")
    print("=" * 60)
    try:
        test_with_openai_client()
    except Exception as e:
        print(f"Error: {e}")

