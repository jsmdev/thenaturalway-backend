#!/usr/bin/env python
"""
Genera un dashboard HTML con todos los reportes de calidad de código.
"""
import json
from pathlib import Path
from datetime import datetime

# Colores para los scores
COLORS = {
    "A": "#22c55e",  # green
    "B": "#84cc16",  # lime
    "C": "#eab308",  # yellow
    "D": "#f97316",  # orange
    "E": "#ef4444",  # red
    "F": "#dc2626",  # dark red
    "HIGH": "#dc2626",
    "MEDIUM": "#f97316",
    "LOW": "#eab308",
}

# Explicaciones en español
METRIC_INFO = {
    "complexity": {
        "title": "Complejidad Ciclomática",
        "description": "Mide el número de caminos independientes a través del código. Mayor complejidad = más difícil de mantener y probar.",
        "optimal": "A-B (1-10): Código simple y fácil de mantener",
        "warning": "C-D (11-20): Considerar refactorizar",
        "critical": "E-F (>20): Refactorizar urgente - código muy complejo",
    },
    "maintainability": {
        "title": "Índice de Mantenibilidad",
        "description": "Calcula qué tan fácil es mantener el código (0-100). Considera complejidad, volumen y comentarios.",
        "optimal": "A (20-100): Código muy mantenible",
        "warning": "B (10-19): Mantenibilidad moderada",
        "critical": "C (0-9): Difícil de mantener - refactorizar",
    },
    "security": {
        "title": "Análisis de Seguridad",
        "description": "Detecta vulnerabilidades de seguridad comunes (SQL injection, XSS, contraseñas hardcoded, etc.).",
        "optimal": "0 issues HIGH/MEDIUM: Código seguro",
        "warning": "1-5 MEDIUM: Revisar y corregir",
        "critical": "HIGH issues: Corregir inmediatamente",
    },
    "pylint": {
        "title": "Pylint Score",
        "description": "Análisis exhaustivo de estilo, errores y code smells. Penaliza cada problema encontrado.",
        "optimal": "8-10: Excelente calidad de código",
        "warning": "6-8: Buena calidad, algunas mejoras",
        "critical": "<6: Muchos problemas - revisar",
    },
    "ruff": {
        "title": "Ruff Linter",
        "description": "Linter ultra-rápido que detecta errores de sintaxis, bugs potenciales y problemas de estilo.",
        "optimal": "0 errores: Código limpio",
        "warning": "<10 warnings: Pocos problemas menores",
        "critical": ">10 errores: Revisar y corregir",
    },
    "dead_code": {
        "title": "Código Muerto",
        "description": "Detecta funciones, clases y variables que nunca se usan. Mantener código muerto dificulta el mantenimiento.",
        "optimal": "<5%: Código limpio y utilizado",
        "warning": "5-10%: Considerar limpiar",
        "critical": ">10%: Eliminar código no usado",
    },
}


def load_json(filepath):
    """Carga un archivo JSON."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_complexity_stats(data):
    """Extrae estadísticas de complejidad."""
    if not data:
        return None

    stats = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    total_complexity = 0
    count = 0
    details = []

    for filename, file_data in data.items():
        for item in file_data:
            if isinstance(item, dict) and "complexity" in item:
                rank = item.get("rank", "A")
                stats[rank] = stats.get(rank, 0) + 1
                total_complexity += item["complexity"]
                count += 1
                
                # Guardar detalles de funciones con complejidad >= C
                if rank in ["C", "D", "E", "F"]:
                    details.append({
                        "file": filename,
                        "name": item.get("name", "unknown"),
                        "type": item.get("type", "F"),
                        "lineno": item.get("lineno", 0),
                        "complexity": item["complexity"],
                        "rank": rank,
                    })

    avg_complexity = total_complexity / count if count > 0 else 0
    
    # Ordenar por complejidad descendente
    details.sort(key=lambda x: x["complexity"], reverse=True)

    return {
        "distribution": stats,
        "average": round(avg_complexity, 2),
        "total_functions": count,
        "details": details[:20],  # Top 20
    }


def get_maintainability_stats(data):
    """Extrae estadísticas de mantenibilidad."""
    if not data:
        return None

    stats = {"A": 0, "B": 0, "C": 0}
    total_mi = 0
    count = 0
    details = []

    for filename, file_data in data.items():
        for item in file_data:
            if isinstance(item, dict) and "mi" in item:
                rank = item.get("rank", "A")
                stats[rank] = stats.get(rank, 0) + 1
                total_mi += item["mi"]
                count += 1
                
                # Guardar archivos con baja mantenibilidad
                if rank in ["B", "C"]:
                    details.append({
                        "file": filename,
                        "mi": round(item["mi"], 2),
                        "rank": rank,
                    })

    avg_mi = total_mi / count if count > 0 else 0
    
    # Ordenar por MI ascendente (peores primero)
    details.sort(key=lambda x: x["mi"])

    return {
        "distribution": stats,
        "average": round(avg_mi, 2),
        "total_files": count,
        "details": details[:20],  # Top 20
    }


def get_security_stats(data):
    """Extrae estadísticas de seguridad."""
    if not data or "results" not in data:
        return None

    stats = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    issues = []

    for result in data["results"]:
        severity = result.get("issue_severity", "LOW")
        stats[severity] = stats.get(severity, 0) + 1
        issues.append(
            {
                "severity": severity,
                "test_id": result.get("test_id", ""),
                "issue_text": result.get("issue_text", ""),
                "filename": result.get("filename", ""),
                "line_number": result.get("line_number", 0),
            }
        )

    return {"distribution": stats, "total_issues": len(issues), "issues": issues[:10]}


def get_pylint_score(data):
    """Extrae el score de Pylint."""
    if not data:
        return None

    # Pylint puede tener diferentes formatos
    if isinstance(data, dict):
        return data.get("score", 0)
    return 0


def get_ruff_stats(data):
    """Extrae estadísticas de Ruff."""
    if not data or not isinstance(data, list):
        return None

    stats = {"error": 0, "warning": 0}
    details = []

    for item in data:
        if isinstance(item, dict):
            code = item.get("code", "")
            message = item.get("message", "")
            filename = item.get("filename", "")
            location = item.get("location", {})
            
            # Clasificar por tipo
            if code.startswith(("E", "F")):  # Errores
                stats["error"] += 1
            else:
                stats["warning"] += 1
            
            details.append({
                "code": code,
                "message": message,
                "file": filename,
                "line": location.get("row", 0),
            })

    return {
        "total": len(data),
        "errors": stats["error"],
        "warnings": stats["warning"],
        "details": details[:30],  # Top 30
    }


def get_dead_code_stats(filepath):
    """Extrae estadísticas de código muerto."""
    try:
        with open(filepath) as f:
            content = f.read()
            lines = content.strip().split("\n")
            
            # Filtrar líneas vacías y líneas con porcentajes
            details = []
            for line in lines:
                if line.strip() and not line.startswith(("#", "//")):
                    # Formato: archivo:linea: mensaje (confianza%)
                    details.append(line.strip())
            
            return {
                "total": len(details),
                "details": details[:30],  # Top 30
            }
    except FileNotFoundError:
        return None


def generate_html(stats):
    """Genera el HTML del dashboard."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complexity = stats.get("complexity")
    maintainability = stats.get("maintainability")
    security = stats.get("security")
    pylint_score = stats.get("pylint_score", 0)

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Calidad de Código</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f3f4f6;
            padding: 20px;
            color: #1f2937;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 32px;
            color: #111827;
            margin-bottom: 10px;
        }}
        .header .timestamp {{
            color: #6b7280;
            font-size: 14px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #374151;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .metric {{
            text-align: center;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        .metric-value {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 14px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .distribution {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}
        .dist-item {{
            flex: 1;
            text-align: center;
            padding: 15px 10px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
        }}
        .dist-label {{
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .dist-value {{
            font-size: 24px;
        }}
        .issue {{
            padding: 15px;
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            border-radius: 4px;
            margin-bottom: 10px;
        }}
        .issue.medium {{
            background: #fff7ed;
            border-left-color: #f97316;
        }}
        .issue.low {{
            background: #fefce8;
            border-left-color: #eab308;
        }}
        .issue-header {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .issue-text {{
            font-size: 14px;
            color: #4b5563;
            margin-bottom: 5px;
        }}
        .issue-location {{
            font-size: 12px;
            color: #6b7280;
        }}
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            font-size: 36px;
            font-weight: bold;
            color: white;
        }}
        .score-label {{
            font-size: 12px;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard de Calidad de Código</h1>
            <div class="timestamp">Generado: {timestamp}</div>
        </div>

        <div class="grid">
"""

    # Complejidad
    if complexity:
        html += f"""
            <div class="card">
                <h2>🔄 Complejidad Ciclomática</h2>
                <div class="metric">
                    <div class="metric-value" style="color: {COLORS.get('B', '#84cc16')}">{complexity['average']}</div>
                    <div class="metric-label">Promedio</div>
                </div>
                <div class="distribution">
"""
        for rank in ["A", "B", "C", "D", "E", "F"]:
            count = complexity["distribution"].get(rank, 0)
            html += f"""
                    <div class="dist-item" style="background: {COLORS.get(rank, '#6b7280')}">
                        <div class="dist-label">{rank}</div>
                        <div class="dist-value">{count}</div>
                    </div>
"""
        html += f"""
                </div>
                <div style="margin-top: 15px; text-align: center; color: #6b7280; font-size: 14px;">
                    Total: {complexity['total_functions']} funciones
                </div>
            </div>
"""

    # Mantenibilidad
    if maintainability:
        mi_color = COLORS["A"] if maintainability["average"] >= 20 else (
            COLORS["B"] if maintainability["average"] >= 10 else COLORS["C"]
        )
        html += f"""
            <div class="card">
                <h2>🔧 Índice de Mantenibilidad</h2>
                <div class="metric">
                    <div class="metric-value" style="color: {mi_color}">{maintainability['average']}</div>
                    <div class="metric-label">Promedio (0-100)</div>
                </div>
                <div class="distribution">
"""
        for rank in ["A", "B", "C"]:
            count = maintainability["distribution"].get(rank, 0)
            html += f"""
                    <div class="dist-item" style="background: {COLORS.get(rank, '#6b7280')}">
                        <div class="dist-label">{rank}</div>
                        <div class="dist-value">{count}</div>
                    </div>
"""
        html += f"""
                </div>
                <div style="margin-top: 15px; text-align: center; color: #6b7280; font-size: 14px;">
                    Total: {maintainability['total_files']} archivos
                </div>
            </div>
"""

    # Pylint Score
    if pylint_score:
        score_color = COLORS["A"] if pylint_score >= 8 else (
            COLORS["C"] if pylint_score >= 6 else COLORS["E"]
        )
        html += f"""
            <div class="card">
                <h2>📝 Pylint Score</h2>
                <div class="score-circle" style="background: {score_color}">
                    {pylint_score:.1f}
                    <div class="score-label">/ 10</div>
                </div>
            </div>
"""

    html += """
        </div>
"""

    # Seguridad (full width)
    if security:
        total = security["total_issues"]
        high = security["distribution"].get("HIGH", 0)
        medium = security["distribution"].get("MEDIUM", 0)
        low = security["distribution"].get("LOW", 0)

        html += f"""
        <div class="card">
            <h2>🔒 Análisis de Seguridad</h2>
            <div class="distribution" style="margin-bottom: 25px;">
                <div class="dist-item" style="background: {COLORS['HIGH']}">
                    <div class="dist-label">HIGH</div>
                    <div class="dist-value">{high}</div>
                </div>
                <div class="dist-item" style="background: {COLORS['MEDIUM']}">
                    <div class="dist-label">MEDIUM</div>
                    <div class="dist-value">{medium}</div>
                </div>
                <div class="dist-item" style="background: {COLORS['LOW']}">
                    <div class="dist-label">LOW</div>
                    <div class="dist-value">{low}</div>
                </div>
            </div>
"""

        if security["issues"]:
            html += "<h3 style='margin-bottom: 15px; font-size: 16px;'>Top 10 Issues</h3>"
            for issue in security["issues"]:
                severity_class = issue["severity"].lower()
                html += f"""
            <div class="issue {severity_class}">
                <div class="issue-header">[{issue['severity']}] {issue['test_id']}</div>
                <div class="issue-text">{issue['issue_text']}</div>
                <div class="issue-location">{issue['filename']}:{issue['line_number']}</div>
            </div>
"""

        html += """
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    return html


def main():
    """Función principal."""
    reports_dir = Path("docs/quality-reports/code-analysis")

    if not reports_dir.exists():
        print("❌ No se encontró el directorio docs/quality-reports/code-analysis/")
        print("   Ejecuta primero: make quality")
        return

    # Cargar datos
    complexity_data = load_json(reports_dir / "complexity.json")
    maintainability_data = load_json(reports_dir / "maintainability.json")
    security_data = load_json(reports_dir / "security.json")
    pylint_data = load_json(reports_dir / "pylint.json")

    # Procesar estadísticas
    stats = {
        "complexity": get_complexity_stats(complexity_data),
        "maintainability": get_maintainability_stats(maintainability_data),
        "security": get_security_stats(security_data),
        "pylint_score": get_pylint_score(pylint_data),
    }

    # Generar HTML
    html_content = generate_html(stats)

    # Guardar archivo
    output_file = reports_dir / "dashboard.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Dashboard generado: {output_file}")
    print(f"   Abrir en navegador: open {output_file}")


if __name__ == "__main__":
    main()
