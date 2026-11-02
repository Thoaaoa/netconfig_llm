import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

reponse = client.chat.complete(
    model="mistral-large-4",
    messages=[{"role": "user", "content": "réponds rapidement a la multiplication 6x1"}],
)


reflexion = []
reponse_finale = []

for bloc in reponse.choices[0].message.content:
    if bloc.type == "thinking":
        reflexion.append(" ".join(morceau.text for morceau in bloc.thinking))
    elif bloc.type == "text":
        reponse_finale.append(bloc.text)

print("REFLEXION:")
print("\n".join(reflexion) or "(aucune)")

print("\nREPONSE")
print("\n".join(reponse_finale))

usage = reponse.usage
print(
    f"\n--- {usage.prompt_tokens} tokens envoyes, "
    f"{usage.completion_tokens} produits, "
    f"arret : {reponse.choices[0].finish_reason}"
)
