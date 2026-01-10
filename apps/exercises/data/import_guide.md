# Guía de Importación de Ejercicios desde Excel/JSON

## Pasos para ejecutar
Abre tu terminal en el directorio del proyecto y ejecuta:

1. Asegúrate de estar en el directorio del proyecto:

> `cd /Users/jsmdev/Developer/jsmdev/thenaturalway-backend`

2. Activa el entorno virtual:
> `source venv/bin/activate`

3. Ejecuta el comando de seed para crear MovementType y Equipment:
> `python3 manage.py seed_movement_types`

4. Valida la importación con dry-run:
> `python3 manage.py import_exercises apps/exercises/data/exercises_import_liberto_mes_1.json --dry-run`

5. Importa los ejercicios:
> `python3 manage.py import_exercises apps/exercises/data/exercises_import_liberto_mes_1.json`

## Formato JSON para Importación

### Estructura del JSON

El archivo JSON debe ser un **array de objetos**, donde cada objeto representa un ejercicio.

### Campos Disponibles

| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `name` | string | ✅ **Sí** | Nombre del ejercicio (máx. 255 caracteres) | `"Press de banca"` |
| `description` | string | ❌ No | Descripción general del ejercicio | `"Ejercicio de fuerza para pectorales..."` |
| `movement_type` | string | ❌ No | Tipo de movimiento (por **nombre**, no display_name) | `"push"`, `"pull"`, `"squat"` |
| `primary_muscle_group` | string | ❌ No | Grupo muscular principal (por **nombre**, no display_name) | `"chest"`, `"quadriceps"` |
| `secondary_muscle_groups` | array[string] | ❌ No | Lista de grupos musculares secundarios (por **nombre**) | `["shoulders", "triceps"]` |
| `equipment` | string | ❌ No | Equipamiento necesario (por **nombre**, no display_name) | `"barbell"`, `"dumbbell"`, `"bodyweight"` |
| `difficulty` | string | ❌ No | Nivel de dificultad. Valores: `"beginner"`, `"intermediate"`, `"advanced"` | `"intermediate"` |
| `instructions` | string | ❌ No | Instrucciones paso a paso del ejercicio | `"1. Paso uno\n2. Paso dos..."` |
| `image_url` | string (URL) | ❌ No | URL de la imagen del ejercicio | `"https://example.com/image.jpg"` |
| `video_url` | string (URL) | ❌ No | URL del video del ejercicio | `"https://example.com/video.mp4"` |
| `is_active` | boolean | ❌ No | Si el ejercicio está activo (por defecto: `true`) | `true` |

### Valores Válidos para Campos de Relación

#### `movement_type`
Usa el campo **`name`** (no `display_name`) del modelo `MovementType`. Ejemplos comunes:
- `"push"`, `"pull"`, `"squat"`, `"hinge"`, `"carry"`, etc.

#### `primary_muscle_group`
Usa el campo **`name`** (no `display_name`) del modelo `MuscleGroup`. Ejemplos comunes:
- `"chest"`, `"back"`, `"shoulders"`, `"arms"`, `"legs"`, `"quadriceps"`, `"hamstrings"`, etc.

#### `secondary_muscle_groups`
Array de strings con los **`name`** de los grupos musculares. Ejemplos:
```json
["shoulders", "triceps", "core"]
```

#### `equipment`
Usa el campo **`name`** (no `display_name`) del modelo `Equipment`. Ejemplos comunes:
- `"barbell"`, `"dumbbell"`, `"kettlebell"`, `"bodyweight"`, `"cable"`, `"machine"`, etc.

### Ejemplo Completo

```json
[
  {
    "name": "Press de banca",
    "description": "Ejercicio de fuerza para pectorales, hombros y tríceps.",
    "movement_type": "push",
    "primary_muscle_group": "chest",
    "secondary_muscle_groups": ["shoulders", "triceps"],
    "equipment": "barbell",
    "difficulty": "intermediate",
    "instructions": "1. Acuéstate en el banco\n2. Sujeta la barra\n3. Baja controladamente\n4. Empuja hacia arriba",
    "image_url": "https://example.com/images/bench-press.jpg",
    "video_url": "https://example.com/videos/bench-press.mp4",
    "is_active": true
  },
  {
    "name": "Sentadillas",
    "description": "Ejercicio fundamental para piernas.",
    "movement_type": "squat",
    "primary_muscle_group": "quadriceps",
    "secondary_muscle_groups": ["glutes", "hamstrings"],
    "equipment": "bodyweight",
    "difficulty": "beginner",
    "instructions": "1. Párate con los pies separados\n2. Baja doblando las rodillas\n3. Vuelve a la posición inicial",
    "image_url": null,
    "video_url": null,
    "is_active": true
  }
]
```

## Importación desde Excel

### Paso 1: Preparar el Excel

Crea una hoja con las siguientes columnas:

| name | description | movement_type | primary_muscle_group | secondary_muscle_groups | equipment | difficulty | instructions | image_url | video_url | is_active |
|------|-------------|---------------|---------------------|------------------------|-----------|------------|--------------|-----------|-----------|-----------|
| Press de banca | Ejercicio para pectorales | push | chest | shoulders, triceps | barbell | intermediate | 1. Paso uno... | https://... | https://... | TRUE |

**Notas importantes para Excel:**
- `secondary_muscle_groups`: Separa múltiples valores con **coma y espacio** (`, `). Ejemplo: `shoulders, triceps, core`
- `is_active`: Usa `TRUE`/`FALSE` en Excel (se convertirá a boolean)
- Los campos opcionales pueden dejarse vacíos

### Paso 2: Convertir Excel a JSON

#### Opción A: Usando Python (pandas)

```python
import pandas as pd
import json

# Leer Excel
df = pd.read_excel('exercises.xlsx')

# Convertir secondary_muscle_groups de string a lista
df['secondary_muscle_groups'] = df['secondary_muscle_groups'].apply(
    lambda x: [s.strip() for s in str(x).split(',')] if pd.notna(x) and x else []
)

# Convertir is_active de Excel boolean a Python boolean
df['is_active'] = df['is_active'].fillna(True).astype(bool)

# Reemplazar NaN con null para JSON
df = df.replace({pd.NA: None, 'nan': None, '': None})

# Convertir a JSON
json_data = df.to_dict('records')

# Guardar
with open('exercises_import.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)
```

#### Opción B: Usando herramientas online

1. Sube tu archivo Excel a [ConvertCSV](https://www.convertcsv.com/excel-to-json.htm) o similar
2. Configura:
   - Separador de `secondary_muscle_groups`: coma (`,`)
   - Convertir valores vacíos a `null`
3. Descarga el JSON resultante

#### Opción C: Usando Excel directamente

Algunas versiones de Excel permiten exportar a JSON usando Power Query o complementos.

### Paso 3: Validar el JSON

Antes de importar, valida que:
- El JSON es válido (usa un validador online)
- Todos los `name` de ejercicios son únicos
- Los valores de `movement_type`, `primary_muscle_group`, `equipment` existen en la base de datos
- Los valores de `difficulty` son válidos: `"beginner"`, `"intermediate"`, `"advanced"` o `null`
- Las URLs son válidas (si se proporcionan)

### Paso 4: Importar a Django

Crea un comando de management para importar:

```python
# apps/exercises/management/commands/import_exercises.py
from django.core.management.base import BaseCommand
import json
from apps.exercises.models import Exercise, MovementType, MuscleGroup, Equipment

class Command(BaseCommand):
    help = 'Import exercises from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    def handle(self, *args, **options):
        with open(options['json_file'], 'r', encoding='utf-8') as f:
            exercises_data = json.load(f)

        created_count = 0
        error_count = 0

        for exercise_data in exercises_data:
            try:
                # Resolver relaciones por nombre
                movement_type = None
                if exercise_data.get('movement_type'):
                    movement_type = MovementType.objects.get(name=exercise_data['movement_type'])

                primary_muscle_group = None
                if exercise_data.get('primary_muscle_group'):
                    primary_muscle_group = MuscleGroup.objects.get(name=exercise_data['primary_muscle_group'])

                equipment = None
                if exercise_data.get('equipment'):
                    equipment = Equipment.objects.get(name=exercise_data['equipment'])

                # Crear ejercicio
                exercise = Exercise.objects.create(
                    name=exercise_data['name'],
                    description=exercise_data.get('description'),
                    movement_type=movement_type,
                    primary_muscle_group=primary_muscle_group,
                    secondary_muscle_groups=exercise_data.get('secondary_muscle_groups', []),
                    equipment=equipment,
                    difficulty=exercise_data.get('difficulty'),
                    instructions=exercise_data.get('instructions'),
                    image_url=exercise_data.get('image_url'),
                    video_url=exercise_data.get('video_url'),
                    is_active=exercise_data.get('is_active', True),
                )

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creado: {exercise.name}')
                )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error en {exercise_data.get("name", "desconocido")}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nImportación completada: {created_count} creados, {error_count} errores'
            )
        )
```

Ejecuta el comando:
```bash
python3 manage.py import_exercises apps/exercises/data/exercises_import.json
```

## Validaciones y Errores Comunes

### Errores Frecuentes

1. **Movimiento/Equipo/Grupo muscular no encontrado**
   - Error: `MovementType matching query does not exist`
   - Solución: Verifica que los nombres coincidan exactamente con los de la BD (usa `name`, no `display_name`)

2. **Valores inválidos en difficulty**
   - Error: `Invalid choice`
   - Solución: Solo usa: `"beginner"`, `"intermediate"`, `"advanced"` o `null`

3. **secondary_muscle_groups no es un array**
   - Error: Al procesar el JSON
   - Solución: Asegúrate de convertir el string de Excel a array en la conversión

4. **Nombre duplicado**
   - Error: `UNIQUE constraint failed`
   - Solución: Los nombres deben ser únicos. Verifica duplicados en el JSON

### Pre-validación

Antes de importar, puedes verificar los datos existentes:

```bash
python3 manage.py shell

from apps.exercises.models import MovementType, MuscleGroup, Equipment

# Ver tipos de movimiento disponibles
print("MovementTypes:", [mt.name for mt in MovementType.objects.all()])

# Ver grupos musculares disponibles
print("MuscleGroups:", [mg.name for mg in MuscleGroup.objects.all()])

# Ver equipamiento disponible
print("Equipment:", [eq.name for eq in Equipment.objects.all()])
```

## Plantilla de Excel

Puedes descargar una plantilla de Excel vacía con las columnas correctas desde:
- `apps/exercises/data/exercises_template.xlsx` (si está disponible)

O crea una hoja con las columnas mencionadas arriba y llénala con tus datos.
