from pydantic import BaseModel, Field
import anthropic

MODELE = "claude-opus-5-5"

# anthropic.Anthropic() lit ANTHROPIC_API_KEY dans l'environnement tout seul.
client = anthropic.Anthropic()


class ConfigurationRouteur(BaseModel):
    routeur: str = Field(
        description="Nom du routeur configure, ex: R1"
    )
    lignes: list[str] = Field(
        description="Les commandes de configuration FRRouting, une par element, dans l'ordre ou les taper, telles qu'elles apparaitraient dans un fichier frr.conf. Inclure la configuration des interfaces ET celle du protocole de routage. "
    )
    explication: list[str] = Field(
        description="Une explication en francais par commande, dans le meme ordre que lignes."
    )


question = (
    "Configure OSPF sur le routeur R1, cible FRRouting. L'interface eth1 porte l'adresse 10.0.0.1/30 et doit etre dans l'aire 0. Le routeur a aussi une interface de loopback lo en 1.1.1.1/32, qui doit elle aussi etre annoncee dans l'aire 0. Le router-id est 1.1.1.1."
)

reponse = client.messages.parse(
    model=MODELE,
    max_tokens=16000,
    messages=[{"role": "user", "content": question}],
    output_format=ConfigurationRouteur,
)

config = reponse.parsed_output

print(f"Routeur : {config.routeur}\n")
for commande, pourquoi in zip(config.lignes, config.explication):
    print(f"{commande:<35} # {pourquoi}")

u = reponse.usage
print(f"\n--- {u.input_tokens} tokens envoyes, {u.output_tokens} produits")
