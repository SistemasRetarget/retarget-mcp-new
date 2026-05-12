"""
Validador de registro de proyectos.
Política: nunca presentar URLs sin verificar HTTP 200 primero.
Si falta información crítica, bloquear y notificar.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent.parent / "PROJECTS" / "REGISTRY.json"

REQUIRED_FIELDS = ["url_production", "url_qa", "service_name_cloudrun", "repo"]


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"REGISTRY.json no encontrado en {REGISTRY_PATH}")
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def verify_url(url: str, timeout: int = 8) -> tuple[bool, int]:
    """Verifica que una URL responde HTTP 200."""
    if not url or url == "PENDIENTE":
        return False, 0
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200, resp.status
    except Exception:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200, resp.status
        except Exception as e:
            return False, 0


def validate_project(project_key: str) -> dict:
    """
    Valida un proyecto del registry.
    Retorna dict con errores, warnings y estado.
    """
    registry = load_registry()
    projects = registry.get("projects", {})

    if project_key not in projects:
        return {
            "ok": False,
            "errors": [f"Proyecto '{project_key}' no existe en REGISTRY.json"],
            "warnings": [],
        }

    project = projects[project_key]
    errors = []
    warnings = []

    # Verificar campos requeridos
    for field in REQUIRED_FIELDS:
        if field not in project or project[field] == "PENDIENTE":
            errors.append(f"Campo '{field}' faltante o PENDIENTE — BLOQUEAR hasta completar")

    # Verificar URLs activas
    for url_key in ["url_production", "url_qa"]:
        url = project.get(url_key, "")
        if url and url != "PENDIENTE":
            ok, code = verify_url(url)
            if not ok:
                errors.append(f"{url_key} ({url}) devuelve {code} — NO presentar esta URL")
            else:
                print(f"  ✓ {url_key}: {url} → {code}")
        else:
            warnings.append(f"{url_key} es PENDIENTE — solicitar al equipo antes de continuar")

    return {
        "ok": len(errors) == 0,
        "project": project.get("name", project_key),
        "errors": errors,
        "warnings": warnings,
    }


def validate_all() -> dict:
    """Valida todos los proyectos del registry."""
    registry = load_registry()
    results = {}
    for key in registry.get("projects", {}):
        print(f"\nValidando: {key}")
        results[key] = validate_project(key)
    return results


if __name__ == "__main__":
    results = validate_all()
    print("\n=== RESULTADO VALIDACIÓN ===")
    for key, result in results.items():
        status = "✅" if result["ok"] else "❌"
        print(f"\n{status} {result['project']}")
        for e in result["errors"]:
            print(f"   ERROR: {e}")
        for w in result["warnings"]:
            print(f"   WARN:  {w}")
