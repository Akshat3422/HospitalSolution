from nemoguardrails import RailsConfig, LLMRails

config = RailsConfig.from_path("src/guardrils")
rails = LLMRails(config)

response = rails.generate(
    messages=[
        {
            "role": "user",
            "content": "My name is Akshat and my phone number is 9876543210."
        }
    ]
)

print(response)