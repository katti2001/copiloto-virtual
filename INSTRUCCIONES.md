# INSTRUCCIONES DE CONFIGURACIÓN Y USO

## 📋 Requisitos Previos

1. **Python 3.7+**
2. **MySQL Server** instalado y corriendo
3. **Cámara web** funcional
4. **Micrófono** funcional
5. **Altavoces** funcionales

---

## 🚀 INICIO RÁPIDO

Una vez configurada la base de datos (ver secciones siguientes):

```bash
# Ejecutar el sistema con interfaz web
python app.py

# O usar el script simplificado
python iniciar.py
```

El sistema abrirá automáticamente tu navegador en `http://localhost:5000`

---

## 🗄️ PASO 1: Configurar Base de Datos MySQL

### Opción A: Usando MySQL Workbench o phpMyAdmin

1. Abre MySQL Workbench o phpMyAdmin
2. Abre el archivo `database_setup.sql`
3. Ejecuta todo el script
4. Verifica que la base de datos `detector_fatiga` se haya creado

### Opción B: Usando línea de comandos

```bash
# Inicia sesión en MySQL
mysql -u root -p

# Ejecuta el script
source database_setup.sql

# O alternativamente
mysql -u root -p < database_setup.sql
```

---

## ⚙️ PASO 2: Configurar Credenciales

1. Abre el archivo `config.yaml`
2. En la sección `database`, configura tus credenciales:

```yaml
database:
  host: localhost
  user: root
  password: "tu_contraseña_mysql_aquí"  # ⚠️ IMPORTANTE: Cambia esto
  database: detector_fatiga
```

---

## 📦 PASO 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## 🚀 PASO 4: Ejecutar el Sistema

### Método 1: Con interfaz web (RECOMENDADO)

```bash
# Opción A: Directamente
python app.py

# Opción B: Con script simplificado
python iniciar.py
```

El sistema:
1. Validará todos los componentes
2. Abrirá automáticamente tu navegador en `http://localhost:5000`
3. Mostrará la interfaz de login

### Método 2: Solo línea de comandos (para pruebas)

```bash
cd src
python main.py
```

---

## 🔐 FLUJO DE AUTENTICACIÓN

El sistema tiene **autenticación de doble factor** con interfaz web:

### Paso 1: Login Web
1. Abre tu navegador en `http://localhost:5000`
2. Ingresa tus credenciales:
   - **Usuario por defecto**: `admin`
   - **Contraseña por defecto**: `admin123`
3. Click en "Encender 🚀"

### Paso 2: Autenticación por Gestos Faciales
Después del login, el sistema te pedirá realizar los siguientes gestos en orden:

1. **Parpadea 3 veces** (cierra ambos ojos)
2. **Guiña el ojo izquierdo 1 vez** (solo el izquierdo)
3. **Baja la cabeza 1 vez** (movimiento hacia abajo)

### Paso 3: Monitor de Fatiga
Una vez autenticado, se iniciará el monitor que:
- Abrirá tu cámara web
- Detectará signos de fatiga en tiempo real
- Registrará eventos en la base de datos
- Te hará preguntas si detecta fatiga

**⚠️ Consejos:**
- Colócate frente a la cámara en un lugar bien iluminado
- Realiza los gestos de forma clara y pausada
- Espera a que el sistema detecte cada gesto antes del siguiente
- Presiona ESC para cancelar

---

## 📊 REQUERIMIENTOS IMPLEMENTADOS

### ✅ Requerimiento 1: Módulo de Autenticación
- **Usuario/Contraseña**: Login tradicional con bcrypt
- **Gestos Faciales**: Autenticación biométrica por gestos
- **Base de datos**: Usuarios almacenados en MySQL

### ✅ Requerimiento 2: Ingestión Multi-modal
- **Video**: Captura continua de frames de cámara (30 FPS)
- **Audio**: Reconocimiento y síntesis de voz
- Funcionan **simultáneamente**

### ✅ Requerimiento 3: Capa de Inferencia
- **MediaPipe**: Detección facial con 468 landmarks
- **Análisis de patrones**: EAR, MAR, pitch, roll, yaw
- **Detección**: Ojos cerrados, bostezos, cabeza abajo
- **Modelo local**: No requiere conexión a internet

### ✅ Requerimiento 4: Lógica de Negocio
- **Máquina de estados**: Normal → Riesgo → Alerta
- **Respuesta automatizada**: Quiz vocal cuando detecta fatiga
- **Feedback adaptativo**: Según estado del usuario

---

## 🗃️ PERSISTENCIA DE DATOS

Todos los eventos se guardan en MySQL:

### Tablas Principales:
1. **usuarios**: Usuarios del sistema
2. **sesiones**: Sesiones de monitoreo
3. **eventos_fatiga**: Eventos de fatiga detectados
4. **respuestas_quiz**: Respuestas a preguntas
5. **logs_sistema**: Logs del sistema
6. **validaciones_sistema**: Validaciones de periféricos

### Al finalizar cada sesión verás:
- Total de eventos detectados
- Cantidad de ojos cerrados
- Cantidad de bostezos
- Cantidad de cabeza abajo
- Alertas activadas

---

## 🔧 VALIDACIONES AL INICIO

El sistema valida **automáticamente**:

✓ **Configuración**: Archivo config.yaml válido  
✓ **Cámara**: Disponible y funcionando  
✓ **Micrófono**: Disponible y funcionando  
✓ **Altavoces**: Disponibles y funcionando  
✓ **Modelo IA**: Descargado (o se descarga automáticamente)  

Si alguna validación falla, el programa **no inicia** y muestra el error.

---

## 👤 CREAR NUEVOS USUARIOS

### Opción A: Desde SQL

```sql
-- Reemplaza 'usuario' y 'contraseña' con los valores deseados
INSERT INTO usuarios (nombre_usuario, hash_contrasena, nombre_completo) 
VALUES ('nuevo_usuario', 
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxHZb7HVm', 
        'Nombre Completo');
```

### Opción B: Desde Python (Recomendado)

```python
from src.database import DatabaseManager

db = DatabaseManager('localhost', 'root', 'tu_password', 'detector_fatiga')
db.connect()

db.create_user("nuevo_usuario", "mi_contraseña_segura", "Nombre Completo")

db.disconnect()
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "No se pudo conectar a la base de datos"
- Verifica que MySQL esté corriendo
- Verifica las credenciales en `config.yaml`
- Ejecuta `database_setup.sql` primero

### Error: "No se pudo abrir la cámara"
- Cierra otras aplicaciones que usen la cámara (Zoom, Teams, etc.)
- Verifica los permisos de la cámara

### Error: "No se encontraron micrófonos"
- Verifica que el micrófono esté conectado
- Revisa la configuración de audio de Windows

### La autenticación por gestos no funciona
- Mejora la iluminación
- Acércate más a la cámara
- Realiza gestos más marcados

---

## 📝 NOTAS ADICIONALES

- El modelo de IA se descarga automáticamente la primera vez (~10 MB)
- Todas las contraseñas se hashean con bcrypt (seguras)
- Los logs se guardan con timestamps precisos
- Presiona **ESC** en cualquier momento para salir

---

## 🎯 ESTRUCTURA DEL PROYECTO

```
copiloto-virtual/
├── src/
│   ├── main.py              # Programa principal integrado
│   ├── auth.py              # Autenticación por gestos
│   ├── database.py          # Gestor de base de datos
│   ├── validator.py         # Validador de sistema
│   ├── detectors.py         # Detectores de fatiga
│   ├── state_machine.py     # Máquina de estados
│   ├── voice.py             # Síntesis y reconocimiento de voz
│   ├── quiz.py              # Generador de preguntas
│   └── ui.py                # Interfaz visual
├── config.yaml              # Configuración
├── database_setup.sql       # Script de base de datos
├── requirements.txt         # Dependencias
└── INSTRUCCIONES.md         # Este archivo
```

---

## 🎓 USO ACADÉMICO

Este proyecto cumple con **todos los requerimientos**:

1. ✅ **Autenticación**: Usuario/contraseña + gestos faciales
2. ✅ **Ingestión Multi-modal**: Video + Audio simultáneos
3. ✅ **Inferencia IA**: MediaPipe local para detección facial
4. ✅ **Lógica de Negocio**: Máquina de estados + respuestas automatizadas
5. ✅ **Persistencia**: MySQL con todas las tablas necesarias
6. ✅ **Validación**: Sistema completo de validación de periféricos

---

¡Listo para usar! 🚀
