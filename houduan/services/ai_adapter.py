"""
AI 模型适配器

支持多种AI模型：通义千问、文心一言、OpenAI GPT等，通过环境变量与配置切换。
"""

from __future__ import annotations

from typing import Optional
import os
import json
import requests

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


def generate_reply_qwen(prompt: str, context: Optional[str] = None) -> str:
    """使用通义千问生成回复"""
    api_key = os.environ.get("QWEN_API_KEY")
    model = os.environ.get("QWEN_MODEL", "qwen-turbo")
    
    if not api_key:
        return "【通义千问】API密钥未配置"
    
    try:
        import dashscope
        from dashscope import Generation
        
        dashscope.api_key = api_key
        
        # 构建输入文本
        input_text = prompt
        if context:
            input_text = f"参考信息：{context}\n\n用户问题：{prompt}"
        
        # 调用通义千问API
        response = Generation.call(
            model=model,
            prompt=f"你是淘宝客服助手，请根据用户问题提供专业、友好的回复。\n\n{input_text}",
            max_tokens=500,
            temperature=0.3
        )
        
        if response.status_code == 200:
            return response.output.text or "【通义千问】生成失败"
        else:
            return f"【通义千问】API调用失败: {response.message}"
            
    except ImportError:
        return "【通义千问】请安装 dashscope: pip install dashscope"
    except Exception as e:
        return f"【通义千问】调用失败: {str(e)}"


def generate_reply_ernie(prompt: str, context: Optional[str] = None) -> str:
    """使用文心一言生成回复"""
    api_key = os.environ.get("ERNIE_API_KEY")
    secret_key = os.environ.get("ERNIE_SECRET_KEY")
    model = os.environ.get("ERNIE_MODEL", "ernie-bot-turbo")
    
    if not api_key or not secret_key:
        return "【文心一言】API密钥未配置"
    
    try:
        import requests
        
        # 获取访问令牌
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        token_params = {
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key
        }
        
        token_response = requests.post(token_url, params=token_params)
        if token_response.status_code != 200:
            return "【文心一言】获取访问令牌失败"
        
        access_token = token_response.json().get("access_token")
        if not access_token:
            return "【文心一言】访问令牌获取失败"
        
        # 构建输入文本
        input_text = prompt
        if context:
            input_text = f"参考信息：{context}\n\n用户问题：{prompt}"
        
        # 调用文心一言API
        api_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}"
        headers = {"Content-Type": "application/json"}
        data = {
            "messages": [
                {"role": "user", "content": f"你是淘宝客服助手，请根据用户问题提供专业、友好的回复。\n\n{input_text}"}
            ],
            "temperature": 0.3,
            "max_output_tokens": 500
        }
        
        response = requests.post(f"{api_url}?access_token={access_token}", 
                               headers=headers, 
                               data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"]
            else:
                return f"【文心一言】API返回错误: {result.get('error_msg', '未知错误')}"
        else:
            return f"【文心一言】API调用失败: {response.status_code}"
            
    except Exception as e:
        return f"【文心一言】调用失败: {str(e)}"


def generate_reply_openai(prompt: str, context: Optional[str] = None) -> str:
    """使用OpenAI GPT生成回复"""
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    
    if not api_key or not OpenAI:
        return "【OpenAI】API密钥未配置或库未安装"
    
    try:
        client = OpenAI(api_key=api_key)
        
        # 构建输入文本
        input_text = prompt
        if context:
            input_text = f"参考信息：{context}\n\n用户问题：{prompt}"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是淘宝客服助手，请根据用户问题提供专业、友好的回复。"},
                {"role": "user", "content": input_text}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content or "【OpenAI】生成失败"
        
    except Exception as e:
        return f"【OpenAI】调用失败: {str(e)}"


def generate_reply(prompt: str, context: Optional[str] = None, model: str = "stub") -> str:
    """生成回复，根据模型类型路由到不同适配器"""
    if not prompt or not prompt.strip():
        return "【错误】请输入有效的问题"
    
    # 根据模型类型选择适配器
    if model == "qwen":
        return generate_reply_qwen(prompt, context)
    elif model == "ernie":
        return generate_reply_ernie(prompt, context)
    elif model == "openai":
        return generate_reply_openai(prompt, context)
    else:
        # 默认占位回复
        base = (context + "\n") if context else ""
        return base + "【AI建议回复】我们已收到您的问题，将尽快为您处理。"


