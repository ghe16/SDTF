# ModSDTFlab - Distributed Systems Algorithm Laboratory

Laboratorio educativo para visualizar y experimentar con algoritmos de sistemas distribuidos (WAL, Paxos, Raft, etc.).

## Requisitos Previos

- **Node.js** (v18 o superior)
- **Python** (v3.10 o superior)
- **pip** (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repositorio>
cd ModSDTFlab
```

### 2. Instalar dependencias del frontend

```bash
npm install
```

### 3. Configurar el backend con entorno virtual

El backend usa un entorno virtual de Python para aislar las dependencias.

#### macOS / Linux

```bash
# Opción 1: Ejecutar script de configuración
./setup.sh

# Opción 2: Manual
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Windows

```powershell
# Opción 1: Manual
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar la Aplicación

Se necesitan dos terminales:

### Terminal 1 - Backend (FastAPI)

```bash
# macOS / Linux
./run_backend.sh

# Windows
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en: `http://localhost:8000`

### Terminal 2 - Frontend (Vite)

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

## Uso de la Aplicación

### 1. Acceder a la interfaz

Abre tu navegador en `http://localhost:5173`

### 2. Seleccionar un algoritmo

En la página principal, selecciona un algoritmo del menú:
- **WAL** - Write-Ahead Logging
- **Paxos** - Algoritmo de consenso
- **Raft** - Algoritmo de consenso

### 3. Configurar parámetros

Cada algoritmo tiene diferentes opciones de configuración:

#### WAL (Write-Ahead Logging)
- **Scenario**: Tipo de escenario a ejecutar
  - `Normal Write`: Operación normal sin crash
  - `Crash After Log`: Crash después de escribir en el log
  - `Multiple Operations`: Múltiples operaciones
  - `Crash After First`: Crash después de la primera operación

#### Paxos / Raft
- **Node Count**: Número de nodos (2-10)
- **Fault Tolerance**: Nodos que pueden fallar (1-3)

### 4. Ejecutar el algoritmo

Haz clic en el botón **Run** para ejecutar el algoritmo.

### 5. Observar los resultados

La interfaz muestra:

| Panel | Descripción |
|-------|-------------|
| **Graph** | Visualización de nodos y conexiones |
| **Timeline** | Línea de tiempo de eventos |
| **Logs** | Registro de eventos durante la ejecución |
| **Results** | Métricas del algoritmo |
| **Validation** | Validación de invariantes |

### 6. Debug (opcional)

Haz clic en el botón **Debug** para ver información detallada del estado del backend.

## Algoritmos Disponibles

### WAL (Write-Ahead Logging)

Sistema de logging que escribe en el log antes de aplicar cambios al almacenamiento. Útil para recuperación ante crashes.

**Flujo:**
```
Client Request → WAL Append → WAL Flush → Storage Apply
                              ↓ (si hay crash)
                    Recovery (replay del log)
```

**Escenarios:**
- Normal Write: operación sin problemas
- Crash After Log: crash entre append y flush
- Multiple Operations: varias operaciones seguidas

### Paxos

Algoritmo de consenso distribuido para acordar un valor entre múltiples nodos.

**Fases:**
1. **Prepare/Promise**: Un nodo propone ser líder
2. **Accept/Accepted**: Se propone y acepta un valor
3. **Decided**: Valor decidido con mayoría

**Invariantes:**
- Safety: No dos nodos deciden valores diferentes
- Liveness: Eventually todo nodo decide
- Validity: El valor decidido fue propuesto

### Raft

Algoritmo de consenso con líder claro y replicación de log.

**Fases:**
1. **Election**: Nodos votan por un líder
2. **Replication**: Leader replica log a seguidores
3. **Commit**: Mayoría confirma entries

**Invariantes:**
- LeaderAppendOnly: Leader solo appende
- LogMatching: Logs idénticos en mismo índice
- ElectionSafety: Un solo líder por término

## Estructura del Proyecto

```
ModSDTFlab/
├── backend/
│   ├── app/
│   │   ├── api/           # Endpoints de la API
│   │   ├── core/
│   │   │   ├── engines/  # Implementaciones de algoritmos
│   │   │   │   ├── wal.py
│   │   │   │   ├── paxos.py
│   │   │   │   ├── raft.py
│   │   │   │   └── mock.py
│   │   │   ├── engine.py # Clase base
│   │   │   └── manager.py
│   │   └── main.py
│   └── requirements.txt
├── src/
│   ├── api/              # Cliente API
│   ├── components/       # Componentes React
│   ├── config/           # Configuración de algoritmos
│   └── pages/            # Páginas de la app
├── package.json
└── README.md
```

## Añadir Nuevos Algoritmos

Para añadir un nuevo algoritmo:

1. Crear un nuevo archivo en `backend/app/core/engines/`
2. Heredar de `AlgorithmEngine`
3. Implementar métodos requeridos:
   - `_create_initial_state()`
   - `step()`
   - `get_result()`
   - `get_validation()`
   - `is_finished()`
4. Registrar con `@register("nombre_algoritmo")`
5. Añadir perfil en `src/config/algorithmProfiles.js`

## Implementación Estudiantil

### WAL Student

El proyecto incluye dos versiones del algoritmo WAL:

1. **wal** (referencia): Implementación completa con solución de referencia
2. **wal-student**: Versión para que estudiantes completen

### Cómo trabajar con wal-student

Los estudiantes deben:

1. **Editar solo este archivo:**
   ```
   backend/app/core/engines/wal_student.py
   ```

2. **No modificar:**
   - La implementación de referencia (`wal.py`)
   - Código del frontend
   - Otros archivos del backend

3. **Completar los TODOs** marcados en el código:
   - `__init__`: Inicializar estado
   - `_create_initial_state`: Configurar estado inicial y grafo
   - `step`: Procesar un paso del algoritmo WAL
   - `_trigger_crash`: Manejar caída del sistema
   - `_do_recovery`: Recuperar entradas comprometidas
   - `get_result`: Retornar métricas
   - `get_validation`: Validar invariantes
   - `is_finished`: Verificar completitud

4. **Ejecutar y probar:**
   - Seleccionar `wal-student` en la interfaz
   - Ejecutar y verificar resultados
   - Revisar que la validación pase

### Comparación de versiones

| Versión | ID en UI | Descripción |
|---------|----------|-------------|
| Referencia | `wal` | Implementación completa |
| Estudiante | `wal-student` | Para completar |

## Troubleshooting

### Error al iniciar el backend

```bash
ModuleNotFoundError: No module named 'fastapi'
```

Solución: Instalar dependencias del backend
```bash
cd backend
pip install -r requirements.txt
```

### Error CORS en el navegador

El backend ya está configurado con CORS. Si persisten errores, verifica que ambos servidores estén ejecutándose en los puertos correctos.

### La ejecución no muestra resultados

1. Verificar que el backend esté corriendo
2. Abrir la consola del navegador (F12) y revisar los logs
3. Hacer clic en "Debug" para ver el estado detallado

## Licencia

MIT