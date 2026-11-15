from pathlib import Path
from pydantic import BaseModel, Field
import anthropic
import subprocess


CONSIGNES = {
    "R1": "Configure OSPF sur le routeur R1, cible FRRouting. L'interface eth1 "
          "porte l'adresse 10.0.0.1/30 et doit etre dans l'aire 0. Le routeur a "
          "aussi une interface de loopback lo en 1.1.1.1/32, annoncee elle aussi "
          "dans l'aire 0. Le router-id est 1.1.1.1.",
    "R2": "Configure OSPF sur le routeur R2, cible FRRouting. L'interface eth1 "
          "porte l'adresse 10.0.0.2/30 et doit etre dans l'aire 0. Le routeur a "
          "aussi une interface de loopback lo en 2.2.2.2/32, annoncee elle aussi "
          "dans l'aire 0. Le router-id est 2.2.2.2.",
}

LABO = Path.home() / "labo-ospf"
CONFIGS = LABO / "configs"
TOPOLOGIE = LABO / "genere.clab.yml"
GABARIT = "frr defaults traditional\n!\n{corps}\n!\n"
MODELE = "claude-opus-5-5"

client = anthropic.Anthropic()


class ConfigurationRouteur(BaseModel):
    routeur: str = Field(
        description="Nom du routeur configure, ex: R1"
    )
    lignes: list[str] = Field(
        description="Les commandes de configuration FRRouting, une par element, "
                    "dans l'ordre ou les taper. Ne pas inclure frr defaults, "
                    "hostname, log, ni les separateurs '!' : le gabarit les ajoute."
    )
    explication: list[str] = Field(
        description="Une explication en francais par commande, dans le meme "
                    "ordre que lignes."
    )


def ecrire(nom, config):
    CONFIGS.mkdir(parents=True, exist_ok=True)
    chemin = CONFIGS / f"{nom}.conf"
    chemin.write_text(GABARIT.format(corps="\n".join(config.lignes)))
    return chemin


def clab(*arguments):
    r = subprocess.run(
        ["sudo", "clab", *arguments, "-t", str(TOPOLOGIE)],
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout + r.stderr


configs = {}

for nom, consigne in CONSIGNES.items():
    reponse = client.messages.parse(
        model=MODELE,
        max_tokens=16000,
        messages=[{"role": "user", "content": consigne}],
        output_format=ConfigurationRouteur,
    )
    config = reponse.parsed_output
    configs[nom] = config

    chemin = ecrire(nom, config)

    print(f"\n{nom} -> {chemin}")
    for commande, pourquoi in zip(config.lignes, config.explication):
        print(f"  {commande:<35} # {pourquoi}")
    u = reponse.usage
    print(f"  {u.input_tokens} tokens envoyes, {u.output_tokens} produits")


print("\nRemise a zero du labo")
clab("destroy", "--graceful")

print("Deploiement")
code, sortie = clab("deploy")
if code != 0:
    print(sortie[-1500:])
    raise SystemExit("le deploiement a echoue")
print("deploye")
