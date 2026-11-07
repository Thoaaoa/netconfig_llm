import os
from pydantic import BaseModel, Field
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

class ConfigurationRouteur(BaseModel):
    routeur: str = Field(
        description="Nom du routeur configure, ex: R1"
    )
    lignes: list[str] = Field(
        description="Les commandes de configuration FRRouting, une par element, dans l'ordre ou les taper. Inclure la configuration des interfaces ET celle du protocole."
    )
    explication: list[str] = Field(
        description="Une explication en francais par commande, dans le meme ordre que lignes."
    )

reponse = client.chat.parse(
    model="mistral-large-4",
    messages=[{"role": "user", "content": "Configure OSPF sur le routeur R1. L’interface eth1 porte l’adresse 10.0.0.1/30 et doit être dans l’aire 0. Le router-id est 1.1.1.1. Cible : FRRouting."}],
    response_format=ConfigurationRouteur
)

config = reponse.choices[0].message.parsed

print(f"Routeur : {config.routeur}\n")
for commande, pk in zip(config.lignes, config.explication):
    print(f"{commande:<35} # {pk}")

u = reponse.usage
print(f"\n--- {u.prompt_tokens} tokens envoyes, {u.completion_tokens} produits")