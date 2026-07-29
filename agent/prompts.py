import yaml
from pathlib import Path


def build_system_prompt():
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    lines = [cfg["persona"], "", "REGLAS:"]
    for r in cfg["reglas"]:
        lines.append(f"- {r}")
    lines.append("")

    fmt = cfg["formato"]
    if not fmt["markdown"]:
        lines.append("- NO uses markdown, asteriscos, negritas ni ningun formato especial.")
    lines.append("- Usa puntuacion natural (puntos, comas). Tu respuesta sera leida en voz alta.")
    if fmt["max_frases_por_defecto"]:
        lines.append(f"- Por defecto, maximo {fmt['max_frases_por_defecto']} frases. Expande solo si el usuario pide mas.")
    lines.append("")
    lines.append("Tu tono es profesional pero cercano, como un companero de trabajo que ensena.")

    return "\n".join(lines)


SYSTEM_PROMPT = build_system_prompt()
