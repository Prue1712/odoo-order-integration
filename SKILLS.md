# SKILLS.md — uso de IA en este proyecto (archivo de la candidata)

Este archivo documenta **cómo se usó inteligencia artificial** (Cursor) para
construir y entender la solución. Es un entregable de **puntos adicionales**
de la prueba: evidencia de uso consciente de IA, no de “copiar sin entender”.

Autora / candidata: cuenta GitHub `Prue1712`  
Herramienta principal: **Cursor** (asistente de desarrollo basado en IA)  
Proyecto: `odoo-order-integration`

---

## 1) Para qué usé la IA

| Uso | Ejemplo concreto |
|-----|------------------|
| Entender el enunciado | Separar “tienda/UI” vs “middleware de integración” |
| Montar el entorno | Docker, WSL2, Odoo 18, Postgres, venv Python |
| Diseñar arquitectura | FastAPI + XML-RPC + 2 Postgres + trazabilidad |
| Generar una primera versión del código base | endpoints, schemas, `order_processor`, `odoo_client` — posteriormente revisada, ajustada y validada durante las pruebas |
| Documentación de entrega | README, API, diagrama, SQL, Oracle, `AGENTS.md` |
| Aprender a explicar | ensayos de demo, mapa de archivos, anti-duplicados |
| Extensiones | campos extra de cliente (`phone`, `mobile`, etc.) |

---

## 2) Qué hice YO (no la IA sola)

- Entregar el escenario de negocio y decidir seguir con la prueba.
- Activar virtualización / WSL / Ubuntu / Docker en la máquina.
- Crear la base Odoo `odoo18`, instalar **Ventas**, crear producto `PROD-001`.
- Probar en Swagger: GET estado, GET logs, POST órdenes.
- Verificar en Odoo las órdenes (`S00001`, `S00002`, `S00003`, …).
- Preguntar y corregir el modelo mental (“no es una tienda, es un puente”).
- Pedir y validar campos adicionales del cliente en la ficha de Odoo.
- Corregir errores encontrados durante las pruebas.
- Validar la integración extremo a extremo (API → Odoo → logs / SQL).
- Ajustar la solución hasta cumplir los requerimientos de la prueba.
- Publicar el repo en GitHub: https://github.com/Prue1712/odoo-order-integration

La IA acelera; **la candidata opera, valida y explica**.

---

## 3) Decisiones técnicas que sí sé defender

1. **Middleware fuera de Odoo** — facilita logs, idempotencia y demo.
2. **XML-RPC** — estándar Odoo, suficiente para la prueba.
3. **Dos Postgres** — `:5432` Odoo / `:5433` integración (trazabilidad).
4. **`external_order_id`** — clave de negocio anti-duplicados.
5. **`client_order_ref`** — deja el ID externo visible en la orden de venta.
6. **Reintento solo si `failed`** — si `created`, no se vuelve a crear.

---

## 4) Metodología de trabajo con IA

1. Pedir explicación en lenguaje simple cuando no entendía.
2. Pedir cambios pequeños y localizados (un archivo / un campo).
3. Probar siempre en Swagger + Odoo antes de dar por bueno.
4. Pedir “dónde tocar si me piden X” para la entrevista.
5. Mantener archivos propios de estudio: `BITACORA-ESTUDIO.txt`, `EJERCICIOS-ENTREVISTA.txt`, este `SKILLS.md`.

---

## 5) Habilidades (skills) que practiqué en la prueba

| Skill | Evidencia en el repo |
|-------|----------------------|
| Integración API ↔ ERP | `app/services/odoo_client.py`, `order_processor.py` |
| Validación de datos | `app/schemas/order.py` |
| Persistencia / SQL | `app/db/*`, `sql/queries.sql` |
| Diseño de arquitectura | `docs/diagram.md`, `README.md` |
| Documentar para humanos e IA | `AGENTS.md`, `docs/API.md` |
| Uso responsable de IA | este archivo + bitácora |

---

## 6) Cómo crear / actualizar este archivo (para la candidata)

1. En la raíz del repo crea `SKILLS.md` (este archivo).
2. Escribe en **tu voz**: qué pediste, qué entendiste, qué probaste.
3. Actualiza cuando agregues algo nuevo (ej. campos de cliente).
4. No inventes: solo lo que realmente hiciste.
5. Sube el cambio a GitHub con el resto de la entrega.

Comando mental: *“Si no lo puedo explicar en la entrevista, no va en SKILLS.md.”*

---

## 7) Relación con otros archivos

| Archivo | Rol |
|---------|-----|
| `AGENTS.md` | Guía para que una IA/persona extienda el proyecto |
| `SKILLS.md` | Guía de **cómo usé IA** y qué aprendí (este) |
| `BITACORA-ESTUDIO.txt` | Notas personales de estudio |
| `EJERCICIOS-ENTREVISTA.txt` | Ensayo oral |

---

## 8) Lecciones aprendidas

Durante el desarrollo reforcé conceptos relacionados con:

- Integración entre sistemas mediante APIs.
- Consumo de servicios XML-RPC en Odoo.
- Validación de datos antes de persistir información.
- Diseño de soluciones desacopladas.
- Importancia de la trazabilidad e idempotencia en procesos de integración.
- Documentación técnica orientada tanto a desarrolladores como a herramientas de IA.

---

## 9) Nota: esto NO es un “Cursor Skill” de producto

Cursor también tiene *Agent Skills* (`SKILL.md` en `.cursor/skills/`) para
automatizar flujos del editor. **Eso es otra cosa.**

Para la prueba técnica, lo que suman puntos es documentar el uso de IA en el
proyecto con archivos propios como este `SKILLS.md`.
