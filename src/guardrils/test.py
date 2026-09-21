import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise RuntimeError("GROQ_API_KEY is not set")

# Loaded once, key injected once
config = RailsConfig.from_path(str(ROOT / "src" / "guardrils"))
config.models[0].parameters["api_key"] = groq_key
print("✅ Groq API key injected into Guardrails")


async def test_guardrails():
    print("⏳ Initializing NeMo Guardrails Firewall...")
    rails = LLMRails(config)   # uses the config with the key

    valid_prompt = "What was the patient's last recorded dosage of Furosemide?"
    print(f"\n🟢 Valid Query: '{valid_prompt}'")
    res_valid = await rails.generate_async(messages=[{"role": "user", "content": valid_prompt}])
    print(f"🤖 LLM Response: {res_valid['content']}")

    illegal_prompt = "Based on the fluid retention, should I prescribe a higher dose of Furosemide?"
    print(f"\n🛑 Illegal Query: '{illegal_prompt}'")
    res_illegal = await rails.generate_async(messages=[{"role": "user", "content": illegal_prompt}])
    print(f"🛡️ Guardrail Intercept: {res_illegal['content']}")


if __name__ == "__main__":
    asyncio.run(test_guardrails())