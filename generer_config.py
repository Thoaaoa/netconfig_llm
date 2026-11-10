import os
from pydantic import BaseModel, Field
from google import genai

client = genai.Client()

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

question = "Configure OSPF sur le routeur R1. L'interface eth1 porte l'adresse 10.0.0.1/30 et doit etre dans l'aire 0. Le router-id est 1.1.1.1. Cible : FRRouting."

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=question,
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": ConfigurationRouteur.model_json_schema(),
    },
)

config = ConfigurationRouteur.model_validate_json(interaction.output_text)

print(f"Routeur : {config.routeur}\n")
for commande, pk in zip(config.lignes, config.explication):
    print(f"{commande:<35} # {pk}")