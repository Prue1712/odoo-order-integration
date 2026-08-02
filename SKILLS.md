# SKILLS.md — Cómo utilicé IA durante este proyecto

Este documento explica cómo utilicé inteligencia artificial durante el desarrollo de esta prueba técnica. Mi intención es mostrar de forma transparente en qué me apoyé con la IA, qué decisiones tomé yo y cómo validé la solución.

**Autora:** GitHub **Prue1712**
**Herramienta utilizada:** Cursor (asistente de desarrollo basado en IA)
**Proyecto:** `odoo-order-integration`

---

# 1. ¿Para qué utilicé la IA?

Durante el desarrollo utilicé la IA como una herramienta de apoyo para acelerar el aprendizaje y resolver dudas técnicas.

La usé para:

* Entender mejor el enunciado y definir el alcance de la solución.
* Configurar el entorno de desarrollo (Docker, WSL2, Odoo 18 y PostgreSQL).
* Diseñar la arquitectura del proyecto.
* Generar una primera versión de algunos archivos, que después revisé, adapté y probé.
* Elaborar la documentación de entrega.
* Preparar la explicación técnica para la entrevista.
* Resolver dudas sobre Odoo, FastAPI, XML-RPC y SQL mientras desarrollaba la solución.

---

# 2. ¿Qué hice yo?

Aunque utilicé IA como apoyo, el desarrollo del proyecto requirió trabajo y validaciones por mi parte.

Durante la prueba:

* Configuré el entorno de desarrollo.
* Instalé Odoo 18 y el módulo de Ventas.
* Creé la base de datos **odoo18**.
* Creé los productos utilizados para las pruebas.
* Probé cada endpoint desde Swagger.
* Validé que las órdenes realmente se crearan en Odoo.
* Corregí errores que fueron apareciendo durante el desarrollo.
* Ajusté la solución hasta cumplir todos los requerimientos de la prueba.
* Agregué nuevos campos para clientes cuando fue necesario.
* Revisé las consultas SQL y confirmé que la trazabilidad quedara registrada correctamente.
* Publiqué el proyecto en GitHub.

Durante el desarrollo también cambié mi forma de entender el problema. Al principio pensaba en una aplicación tipo tienda, pero después comprendí que realmente se trataba de construir un middleware de integración entre un sistema externo y Odoo.

> La IA me ayudó a avanzar más rápido, pero todas las pruebas, validaciones y decisiones finales las hice yo.

---

# 3. Decisiones técnicas que puedo explicar

Durante la entrevista puedo explicar por qué tomé estas decisiones:

* Implementar un middleware independiente de Odoo.
* Utilizar FastAPI para exponer la API.
* Integrar con Odoo mediante XML-RPC.
* Mantener una base de datos para Odoo y otra para la trazabilidad de la integración.
* Utilizar `external_order_id` para evitar órdenes duplicadas.
* Guardar el identificador externo en `client_order_ref`.
* Permitir reintentos únicamente cuando una integración terminó con estado **failed**.

---

# 4. Cómo trabajé con la IA

Mientras desarrollaba el proyecto seguí una forma de trabajo sencilla:

* Pedía explicaciones cuando no entendía algún concepto.
* Hacía cambios pequeños para comprender qué estaba modificando.
* Probaba cada cambio antes de continuar.
* Verificaba el resultado tanto en Swagger como directamente en Odoo.
* Preguntaba qué archivo debía modificar cuando quería agregar una nueva funcionalidad.
* Mantuve notas propias para estudiar y preparar la entrevista.

---

# 5. Habilidades que reforcé

Durante esta prueba practiqué principalmente:

* Integración entre APIs y Odoo.
* Validación de datos.
* Python.
* SQL y PostgreSQL.
* Consumo de XML-RPC.
* Diseño de una arquitectura de integración.
* Documentación técnica.
* Uso responsable de herramientas de IA.

---

# 6. Documentación relacionada

Este proyecto incluye varios documentos que se complementan entre sí:

* **AGENTS.md:** explica cómo funciona la solución y cómo extenderla.
* **SKILLS.md:** documenta cómo utilicé la IA durante el desarrollo.
* **BITACORA-ESTUDIO.txt:** contiene mis notas de estudio.
* **EJERCICIOS-ENTREVISTA.txt:** me ayudó a preparar la explicación del proyecto.

---

# 7. Lo que aprendí

Esta prueba me permitió reforzar conocimientos sobre:

* Integración entre sistemas mediante APIs.
* Comunicación con Odoo usando XML-RPC.
* Validación de información antes de crear registros.
* Diseño de soluciones desacopladas.
* Importancia de la trazabilidad y de evitar duplicados.
* Documentación técnica.
* Uso de inteligencia artificial como una herramienta de apoyo, entendiendo siempre el código y validando el resultado.

---

# 8. Nota

Este archivo no corresponde a los **Agent Skills** propios de Cursor.

Su objetivo es documentar de forma transparente cómo utilicé la inteligencia artificial durante el desarrollo del proyecto y demostrar que comprendo las decisiones técnicas tomadas.

Como regla personal seguí una idea durante toda la prueba:

> **Si no puedo explicarlo durante la entrevista, entonces no hace parte de mi solución.**
