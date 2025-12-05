#!/usr/bin/env python
"""
Genera un dashboard HTML completo con todos los reportes de calidad de código.
Incluye explicaciones en español y valores óptimos para cada métrica.
"""
import json
from datetime import datetime
from pathlib import Path

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
        "icon": "🔄",
        "description": "Mide el número de caminos independientes a través del código. Mayor complejidad = más difícil de mantener y probar.",
        "optimal": "✅ A-B (1-10): Código simple y fácil de mantener",
        "warning": "⚠️ C-D (11-20): Considerar refactorizar",
        "critical": "❌ E-F (>20): Refactorizar urgente - código muy complejo",
    },
    "maintainability": {
        "title": "Índice de Mantenibilidad",
        "icon": "🔧",
        "description": "Calcula qué tan fácil es mantener el código (0-100). Considera complejidad, volumen y comentarios.",
        "optimal": "✅ A (20-100): Código muy mantenible",
        "warning": "⚠️ B (10-19): Mantenibilidad moderada",
        "critical": "❌ C (0-9): Difícil de mantener - refactorizar",
    },
    "security": {
        "title": "Análisis de Seguridad",
        "icon": "🔒",
        "description": "Detecta vulnerabilidades de seguridad comunes (SQL injection, XSS, contraseñas hardcoded, etc.).",
        "optimal": "✅ 0 issues HIGH/MEDIUM: Código seguro",
        "warning": "⚠️ 1-5 MEDIUM: Revisar y corregir",
        "critical": "❌ HIGH issues: Corregir inmediatamente",
    },
    "pylint": {
        "title": "Pylint Score",
        "icon": "📝",
        "description": "Análisis exhaustivo de estilo, errores y code smells. Penaliza cada problema encontrado.",
        "optimal": "✅ 8-10: Excelente calidad de código",
        "warning": "⚠️ 6-8: Buena calidad, algunas mejoras",
        "critical": "❌ <6: Muchos problemas - revisar",
    },
    "ruff": {
        "title": "Ruff Linter",
        "icon": "⚡",
        "description": "Linter ultra-rápido que detecta errores de sintaxis, bugs potenciales y problemas de estilo.",
        "optimal": "✅ 0 errores: Código limpio",
        "warning": "⚠️ <10 warnings: Pocos problemas menores",
        "critical": "❌ >10 errores: Revisar y corregir",
    },
    "dead_code": {
        "title": "Código Muerto",
        "icon": "💀",
        "description": "Detecta funciones, clases y variables que nunca se usan. Mantener código muerto dificulta el mantenimiento.",
        "optimal": "✅ <10 items: Código limpio y utilizado",
        "warning": "⚠️ 10-30 items: Considerar limpiar",
        "critical": "❌ >30 items: Eliminar código no usado",
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
                    details.append(
                        {
                            "file": filename,
                            "name": item.get("name", "unknown"),
                            "type": item.get("type", "F"),
                            "lineno": item.get("lineno", 0),
                            "complexity": item["complexity"],
                            "rank": rank,
                        }
                    )

    avg_complexity = total_complexity / count if count > 0 else 0

    # Ordenar por complejidad descendente
    details.sort(key=lambda x: x["complexity"], reverse=True)

    return {
        "distribution": stats,
        "average": round(avg_complexity, 2),
        "total_functions": count,
        "details": details[:30],  # Top 30
    }


def get_maintainability_stats(data):
    """Extrae estadísticas de mantenibilidad."""
    if not data:
        return None

    stats = {"A": 0, "B": 0, "C": 0}
    total_mi = 0
    count = 0
    details = []

    # El JSON tiene formato: {archivo: {mi: ..., rank: ...}}
    for filename, file_data in data.items():
        # file_data es un dict, no una lista
        if isinstance(file_data, dict) and "mi" in file_data:
            rank = file_data.get("rank", "A")
            stats[rank] = stats.get(rank, 0) + 1
            total_mi += file_data["mi"]
            count += 1

            # Guardar archivos con baja mantenibilidad
            if rank in ["B", "C"]:
                details.append(
                    {
                        "file": filename,
                        "mi": round(file_data["mi"], 2),
                        "rank": rank,
                    }
                )

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

    return {"distribution": stats, "total_issues": len(issues), "issues": issues[:15]}


def get_pylint_stats(data):
    """Extrae estadísticas de Pylint."""
    if not data:
        return None

    # Pylint devuelve un array de issues
    if isinstance(data, list):
        stats = {"convention": 0, "warning": 0, "error": 0, "refactor": 0}
        details = []

        for item in data:
            if isinstance(item, dict):
                issue_type = item.get("type", "convention")
                stats[issue_type] = stats.get(issue_type, 0) + 1

                details.append(
                    {
                        "type": issue_type,
                        "symbol": item.get("symbol", ""),
                        "message": item.get("message", ""),
                        "file": item.get("path", ""),
                        "line": item.get("line", 0),
                    }
                )

        # Calcular score simple: 10 - (total issues / 100)
        total_issues = sum(stats.values())
        score = max(0, 10 - (total_issues / 100))

        return {
            "score": round(score, 2),
            "total_issues": total_issues,
            "stats": stats,
            "details": details[:30],  # Top 30
        }

    # Si viene un dict con score (formato antiguo)
    if isinstance(data, dict):
        return {"score": data.get("score", 0), "total_issues": 0, "stats": {}, "details": []}

    return None


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

            details.append(
                {
                    "code": code,
                    "message": message,
                    "file": filename,
                    "line": location.get("row", 0),
                }
            )

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

            # Filtrar líneas vacías
            details = []
            for line in lines:
                if line.strip() and not line.startswith(("#", "//")):
                    details.append(line.strip())

            return {
                "total": len(details),
                "details": details[:30],  # Top 30
            }
    except FileNotFoundError:
        return None


def generate_metric_card(section_id, info, stats, details_html="", collapsible=True):
    """Genera una tarjeta de métrica con explicación."""
    collapse_button = (
        f"""
        <button class="collapse-btn" onclick="toggleSection('{section_id}')">
            <span class="collapse-icon" id="icon-{section_id}">▼</span>
        </button>
    """
        if collapsible
        else ""
    )

    return f"""
        <div id="{section_id}" class="card full-width section">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2>{info['icon']} {info['title']}</h2>
                {collapse_button}
            </div>
            <div id="content-{section_id}" class="section-content">
                <div class="metric-description">
                    <p><strong>¿Qué mide?</strong> {info['description']}</p>
                    <div class="metric-thresholds">
                        <div>{info['optimal']}</div>
                        <div>{info['warning']}</div>
                        <div>{info['critical']}</div>
                    </div>
                </div>
                {stats}
                {details_html}
            </div>
        </div>
    """


def generate_html(stats):
    """Genera el HTML del dashboard."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complexity = stats.get("complexity")
    maintainability = stats.get("maintainability")
    security = stats.get("security")
    pylint = stats.get("pylint")
    ruff = stats.get("ruff")
    dead_code = stats.get("dead_code")

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
            color: #1f2937;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}
        html {{
            scroll-behavior: smooth;
        }}
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 260px;
            height: 100vh;
            background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
            padding: 30px 20px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }}
        .sidebar-logo {{
            color: white;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .sidebar-subtitle {{
            color: #9ca3af;
            font-size: 12px;
            margin-bottom: 30px;
        }}
        .sidebar-nav {{
            list-style: none;
        }}
        .sidebar-nav li {{
            margin-bottom: 8px;
        }}
        .sidebar-nav a {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            color: #d1d5db;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.2s;
            font-size: 14px;
        }}
        .sidebar-nav a:hover {{
            background: rgba(255,255,255,0.1);
            color: white;
            transform: translateX(4px);
        }}
        .sidebar-nav a.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
        }}
        .sidebar-nav .icon {{
            font-size: 18px;
            width: 24px;
            text-align: center;
        }}
        .main-content {{
            margin-left: 260px;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            color: white;
        }}
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .header .timestamp {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .card {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .card.full-width {{
            grid-column: 1 / -1;
        }}
        .card h2 {{
            font-size: 22px;
            margin-bottom: 20px;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        .metric-description {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }}
        .metric-description p {{
            margin-bottom: 15px;
            color: #374151;
        }}
        .metric-thresholds {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            font-size: 14px;
        }}
        .metric-thresholds div {{
            padding: 8px 12px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #e5e7eb;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric {{
            text-align: center;
            padding: 25px;
            background: #f9fafb;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .metric-value {{
            font-size: 56px;
            font-weight: bold;
            margin-bottom: 8px;
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
            margin-bottom: 20px;
        }}
        .dist-item {{
            flex: 1;
            text-align: center;
            padding: 18px 10px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
        }}
        .dist-label {{
            font-size: 13px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .dist-value {{
            font-size: 28px;
        }}
        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }}
        .details-table th {{
            background: #f3f4f6;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
        }}
        .details-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .details-table tr:hover {{
            background: #f9fafb;
        }}
        .rank-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
        .issue {{
            padding: 15px;
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            border-radius: 4px;
            margin-bottom: 12px;
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
            margin-bottom: 6px;
            font-size: 14px;
        }}
        .issue-text {{
            font-size: 13px;
            color: #4b5563;
            margin-bottom: 6px;
        }}
        .issue-location {{
            font-size: 12px;
            color: #6b7280;
            font-family: 'Courier New', monospace;
        }}
        .score-circle {{
            width: 140px;
            height: 140px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 48px;
            font-weight: bold;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}
        .score-label {{
            font-size: 14px;
            margin-top: 5px;
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .summary-item {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-item strong {{
            display: block;
            font-size: 32px;
            margin-bottom: 5px;
        }}
        .summary-item span {{
            color: #6b7280;
            font-size: 14px;
        }}
        code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .section {{
            scroll-margin-top: 20px;
        }}
        .collapse-btn {{
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #6b7280;
            transition: transform 0.3s;
            padding: 8px;
            border-radius: 4px;
        }}
        .collapse-btn:hover {{
            background: #f3f4f6;
            color: #374151;
        }}
        .collapse-icon {{
            display: inline-block;
            transition: transform 0.3s;
        }}
        .collapse-icon.collapsed {{
            transform: rotate(-90deg);
        }}
        .section-content {{
            transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
            overflow: hidden;
        }}
        .section-content.collapsed {{
            max-height: 0 !important;
            opacity: 0;
        }}
    </style>
    <script>
        // Toggle section collapse
        function toggleSection(sectionId) {{
            const content = document.getElementById(`content-${{sectionId}}`);
            const icon = document.getElementById(`icon-${{sectionId}}`);

            if (content.classList.contains('collapsed')) {{
                content.classList.remove('collapsed');
                icon.classList.remove('collapsed');
                content.style.maxHeight = content.scrollHeight + 'px';
            }} else {{
                content.style.maxHeight = content.scrollHeight + 'px';
                setTimeout(() => {{
                    content.classList.add('collapsed');
                    icon.classList.add('collapsed');
                }}, 10);
            }}
        }}

        // Activar el link de navegación correspondiente al hacer scroll
        document.addEventListener('DOMContentLoaded', function() {{
            // Set initial max-height for all sections
            document.querySelectorAll('.section-content').forEach(content => {{
                content.style.maxHeight = content.scrollHeight + 'px';
            }});
            const sections = document.querySelectorAll('.section');
            const navLinks = document.querySelectorAll('.nav-link');

            // Resaltar sección activa en el menú
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const id = entry.target.getAttribute('id');
                        navLinks.forEach(link => {{
                            link.classList.remove('active');
                            if (link.getAttribute('href') === `#${{id}}`) {{
                                link.classList.add('active');
                            }}
                        }});
                    }}
                }});
            }}, {{
                threshold: 0.3,
                rootMargin: '-100px 0px -50% 0px'
            }});

            sections.forEach(section => observer.observe(section));
        }});
    </script>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-logo">
            📊 Quality Dashboard
        </div>
        <div class="sidebar-subtitle">The Natural Way Backend</div>

        <ul class="sidebar-nav">
            <li><a href="#overview" class="nav-link"><span class="icon">📄</span> Resumen</a></li>
            <li><a href="#complexity" class="nav-link"><span class="icon">🔄</span> Complejidad</a></li>
            <li><a href="#maintainability" class="nav-link"><span class="icon">🔧</span> Mantenibilidad</a></li>
            <li><a href="#pylint" class="nav-link"><span class="icon">📝</span> Pylint</a></li>
            <li><a href="#ruff" class="nav-link"><span class="icon">⚡</span> Ruff</a></li>
            <li><a href="#security" class="nav-link"><span class="icon">🔒</span> Seguridad</a></li>
            <li><a href="#dead-code" class="nav-link"><span class="icon">💀</span> Código Muerto</a></li>
        </ul>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <div class="container">
            <div class="header">
                <h1>📊 Dashboard de Calidad de Código</h1>
                <div class="timestamp">Generado: {timestamp}</div>
            </div>

            <!-- Project Overview -->
            <div id="overview" class="card full-width section" style="margin-bottom: 30px;">
                <h2>📄 The Natural Way - Backend API</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div style="background: #f9fafb; padding: 20px; border-radius: 8px;">
                        <h3 style="font-size: 16px; margin-bottom: 12px; color: #374151;">🛠️ Stack Tecnológico</h3>
                        <ul style="list-style: none; font-size: 14px; line-height: 2;">
                            <li><strong>Python:</strong> 3.13</li>
                            <li><strong>Framework:</strong> Django 5.1+</li>
                            <li><strong>API:</strong> Django REST Framework</li>
                            <li><strong>Auth:</strong> JWT (simplejwt)</li>
                            <li><strong>Database:</strong> SQLite (dev) / PostgreSQL (prod)</li>
                        </ul>
                    </div>
                    <div style="background: #f9fafb; padding: 20px; border-radius: 8px;">
                        <h3 style="font-size: 16px; margin-bottom: 12px; color: #374151;">🎯 Descripción</h3>
                        <p style="font-size: 14px; line-height: 1.8; color: #4b5563;">
                            API REST para una aplicación de fitness tracking. Los usuarios pueden crear rutinas personalizadas de entrenamiento, registrar sesiones de ejercicio y monitorear su progreso a lo largo del tiempo.
                        </p>
                    </div>
                    <div style="background: #f9fafb; padding: 20px; border-radius: 8px;">
                        <h3 style="font-size: 16px; margin-bottom: 12px; color: #374151;">🏛️ Arquitectura</h3>
                        <p style="font-size: 14px; line-height: 1.8; color: #4b5563;">
                            <strong>Capas:</strong> View → Service → Repository<br>
                            <strong>Apps:</strong> users, routines, exercises<br>
                            <strong>Testing:</strong> factory-boy + coverage<br>
                            <strong>Quality:</strong> Ruff + pre-commit hooks
                        </p>
                    </div>
                </div>
            </div>

            <div class="grid">
"""

    # 1. Complejidad Ciclomática
    if complexity:
        info = METRIC_INFO["complexity"]
        stats_html = f"""
            <div class="metric">
                <div class="metric-value" style="color: {COLORS.get('B', '#84cc16')}">{complexity['average']}</div>
                <div class="metric-label">Promedio</div>
            </div>
            <div class="distribution">
        """
        for rank in ["A", "B", "C", "D", "E", "F"]:
            count = complexity["distribution"].get(rank, 0)
            stats_html += f"""
                <div class="dist-item" style="background: {COLORS.get(rank, '#6b7280')}">
                    <div class="dist-label">{rank}</div>
                    <div class="dist-value">{count}</div>
                </div>
            """
        stats_html += f"""
            </div>
            <div class="summary-stats">
                <div class="summary-item">
                    <strong>{complexity['total_functions']}</strong>
                    <span>Funciones analizadas</span>
                </div>
            </div>
        """

        details_html = ""
        if complexity["details"]:
            details_html = """
            <h3 style="margin-top: 25px; margin-bottom: 15px; font-size: 18px;">🔍 Funciones más complejas (requieren refactorización)</h3>
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Archivo</th>
                        <th>Función</th>
                        <th>Línea</th>
                        <th>Complejidad</th>
                        <th>Rank</th>
                    </tr>
                </thead>
                <tbody>
            """
            for item in complexity["details"]:
                details_html += f"""
                    <tr>
                        <td><code>{item['file']}</code></td>
                        <td><strong>{item['name']}</strong></td>
                        <td>{item['lineno']}</td>
                        <td>{item['complexity']}</td>
                        <td><span class="rank-badge" style="background: {COLORS.get(item['rank'], '#6b7280')}">{item['rank']}</span></td>
                    </tr>
                """
            details_html += """
                </tbody>
            </table>
            """

        html += generate_metric_card("complexity", info, stats_html, details_html)

    # 2. Mantenibilidad
    if maintainability:
        info = METRIC_INFO["maintainability"]
        mi_color = (
            COLORS["A"]
            if maintainability["average"] >= 20
            else (COLORS["B"] if maintainability["average"] >= 10 else COLORS["C"])
        )
        stats_html = f"""
            <div class="metric">
                <div class="metric-value" style="color: {mi_color}">{maintainability['average']}</div>
                <div class="metric-label">Promedio (0-100)</div>
            </div>
            <div class="distribution">
        """
        for rank in ["A", "B", "C"]:
            count = maintainability["distribution"].get(rank, 0)
            stats_html += f"""
                <div class="dist-item" style="background: {COLORS.get(rank, '#6b7280')}">
                    <div class="dist-label">{rank}</div>
                    <div class="dist-value">{count}</div>
                </div>
            """
        stats_html += f"""
            </div>
            <div class="summary-stats">
                <div class="summary-item">
                    <strong>{maintainability['total_files']}</strong>
                    <span>Archivos analizados</span>
                </div>
            </div>
        """

        details_html = ""
        if maintainability["details"]:
            details_html = """
            <h3 style="margin-top: 25px; margin-bottom: 15px; font-size: 18px;">⚠️ Archivos con baja mantenibilidad</h3>
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Archivo</th>
                        <th>Índice MI</th>
                        <th>Rank</th>
                    </tr>
                </thead>
                <tbody>
            """
            for item in maintainability["details"]:
                details_html += f"""
                    <tr>
                        <td><code>{item['file']}</code></td>
                        <td>{item['mi']}</td>
                        <td><span class="rank-badge" style="background: {COLORS.get(item['rank'], '#6b7280')}">{item['rank']}</span></td>
                    </tr>
                """
            details_html += """
                </tbody>
            </table>
            """

        html += generate_metric_card("maintainability", info, stats_html, details_html)

    # 3. Pylint
    if pylint:
        info = METRIC_INFO["pylint"]
        score = pylint.get("score", 0)
        score_color = COLORS["A"] if score >= 8 else (COLORS["C"] if score >= 6 else COLORS["E"])
        stats_html = f"""
            <div class="score-circle" style="background: {score_color}">
                {score:.1f}
                <div class="score-label">/ 10</div>
            </div>
            <div class="summary-stats">
                <div class="summary-item">
                    <strong>{pylint['total_issues']}</strong>
                    <span>Total issues</span>
                </div>
                <div class="summary-item" style="background: #fef2f2;">
                    <strong style="color: #dc2626;">{pylint['stats'].get('error', 0)}</strong>
                    <span>Errores</span>
                </div>
                <div class="summary-item" style="background: #fff7ed;">
                    <strong style="color: #f97316;">{pylint['stats'].get('warning', 0)}</strong>
                    <span>Warnings</span>
                </div>
                <div class="summary-item" style="background: #fefce8;">
                    <strong style="color: #eab308;">{pylint['stats'].get('convention', 0)}</strong>
                    <span>Conventions</span>
                </div>
            </div>
        """

        details_html = ""
        if pylint["details"]:
            details_html = """
            <h3 style="margin-top: 25px; margin-bottom: 15px; font-size: 18px;">📝 Issues detectados</h3>
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Tipo</th>
                        <th>Símbolo</th>
                        <th>Mensaje</th>
                        <th>Archivo</th>
                        <th>Línea</th>
                    </tr>
                </thead>
                <tbody>
            """
            for item in pylint["details"][:30]:
                type_color = {
                    "error": "#dc2626",
                    "warning": "#f97316",
                    "convention": "#eab308",
                    "refactor": "#3b82f6",
                }.get(item["type"], "#6b7280")
                details_html += f"""
                    <tr>
                        <td><span style="color: {type_color}; font-weight: bold;">{item['type']}</span></td>
                        <td><code>{item['symbol']}</code></td>
                        <td>{item['message']}</td>
                        <td><code>{item['file']}</code></td>
                        <td>{item['line']}</td>
                    </tr>
                """
            details_html += """
                </tbody>
            </table>
            """

        html += generate_metric_card("pylint", info, stats_html, details_html)

    # 4. Ruff Linter
    if ruff:
        info = METRIC_INFO["ruff"]
        stats_html = f"""
            <div class="summary-stats">
                <div class="summary-item">
                    <strong>{ruff['total']}</strong>
                    <span>Total problemas</span>
                </div>
                <div class="summary-item" style="background: #fef2f2;">
                    <strong style="color: #dc2626;">{ruff['errors']}</strong>
                    <span>Errores</span>
                </div>
                <div class="summary-item" style="background: #fff7ed;">
                    <strong style="color: #f97316;">{ruff['warnings']}</strong>
                    <span>Warnings</span>
                </div>
            </div>
        """

        details_html = ""
        if ruff["details"]:
            details_html = """
            <h3 style="margin-top: 25px; margin-bottom: 15px; font-size: 18px;">⚡ Problemas detectados</h3>
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Mensaje</th>
                        <th>Archivo</th>
                        <th>Línea</th>
                    </tr>
                </thead>
                <tbody>
            """
            for item in ruff["details"][:30]:
                details_html += f"""
                    <tr>
                        <td><code>{item['code']}</code></td>
                        <td>{item['message']}</td>
                        <td><code>{item['file']}</code></td>
                        <td>{item['line']}</td>
                    </tr>
                """
            details_html += """
                </tbody>
            </table>
            """

        html += generate_metric_card("ruff", info, stats_html, details_html)

    html += """
        </div>
    """

    # 5. Seguridad (full width)
    if security:
        info = METRIC_INFO["security"]
        high = security["distribution"].get("HIGH", 0)
        medium = security["distribution"].get("MEDIUM", 0)
        low = security["distribution"].get("LOW", 0)

        stats_html = f"""
            <div class="distribution">
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

        details_html = ""
        if security["issues"]:
            details_html = "<h3 style='margin-top: 25px; margin-bottom: 15px; font-size: 18px;'>🚨 Vulnerabilidades detectadas</h3>"
            for issue in security["issues"]:
                severity_class = issue["severity"].lower()
                details_html += f"""
            <div class="issue {severity_class}">
                <div class="issue-header">[{issue['severity']}] {issue['test_id']}</div>
                <div class="issue-text">{issue['issue_text']}</div>
                <div class="issue-location">{issue['filename']}:{issue['line_number']}</div>
            </div>
                """

        html += generate_metric_card("security", info, stats_html, details_html)

    # 6. Código Muerto
    if dead_code and dead_code["total"] > 0:
        info = METRIC_INFO["dead_code"]
        stats_html = f"""
            <div class="summary-stats">
                <div class="summary-item">
                    <strong>{dead_code['total']}</strong>
                    <span>Items de código no usado</span>
                </div>
            </div>
        """

        details_html = ""
        if dead_code["details"]:
            details_html = """
            <h3 style="margin-top: 25px; margin-bottom: 15px; font-size: 18px;">💀 Código muerto detectado</h3>
            <div style="font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.8;">
            """
            for line in dead_code["details"][:30]:
                details_html += f"<div style='padding: 5px; background: #f9fafb; margin-bottom: 3px; border-radius: 4px;'>{line}</div>"
            details_html += "</div>"

        html += generate_metric_card("dead-code", info, stats_html, details_html)

    html += """
            </div>
        </div>
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

    print("📊 Generando dashboard HTML mejorado...")

    # Cargar datos
    complexity_data = load_json(reports_dir / "complexity.json")
    maintainability_data = load_json(reports_dir / "maintainability.json")
    security_data = load_json(reports_dir / "security.json")
    pylint_data = load_json(reports_dir / "pylint.json")
    ruff_data = load_json(reports_dir / "ruff.json")
    dead_code_data = get_dead_code_stats(reports_dir / "dead-code.txt")

    # Procesar estadísticas
    stats = {
        "complexity": get_complexity_stats(complexity_data),
        "maintainability": get_maintainability_stats(maintainability_data),
        "security": get_security_stats(security_data),
        "pylint": get_pylint_stats(pylint_data),
        "ruff": get_ruff_stats(ruff_data),
        "dead_code": dead_code_data,
    }

    # Generar HTML
    html_content = generate_html(stats)

    # Guardar archivo
    output_file = reports_dir / "dashboard.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Dashboard generado: {output_file}")


if __name__ == "__main__":
    main()
