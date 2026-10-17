# Roadmap (por qué y en qué orden)

Convención: **nombre primero, código entre paréntesis**. Los códigos son etiquetas, no un orden: el orden real es el de esta lista, que está ordenada por riesgo (primero lo que más puede tirar abajo el proyecto).

Las fases, en orden real:

1. ✅ **Voz (S1)** — probado: la voz del harness le gana a Brown sin cambios (VoiceAdherence +0.209, UserIntent +0.217, ambos sobre el ruido). Veredicto: `odd/reports/s1-a2-verdict.md`. Queda FollowsGT en el piso.
2. 🔄 **Arreglos (S1.1)** — parche del slice anterior antes de construir el monorepo. Estado y evidencia: `odd/tasks/s1-1-hardening.md`. Piezas: medición (W0 ✅), gate de slop (W1 ✅), notas de experiencia (W2), terminología (W3), runtime (W4), una corrida S1.1, y tu post real (T10).
3. ⬜ **Monorepo (S0)** — juntar todo en un repo, verificar Python 3.14, chequear la cookie de Substack desde Cloud Run. Construye acá y no antes: no se monta infraestructura sobre una voz que todavía no funciona.
4. ⬜ **Nova lee builds (S2)** — el agente de investigación aprende a leer README, build-log y git history: el caso más difícil (posts de build).
5. ⬜ **Tu MCP (S3)** — servidor FastMCP propio: expone tu voz, el prompt con aprobación humana, y crea el borrador en Substack con imágenes. Acá se cumple "sube mi draft".
6. ⬜ **Deploy (S4)** — Docker + Cloud Run + auth, estilo curso. Lo que pide la certificación.
7. ⬜ **El post del build (S5)** — el post que cuenta este proyecto, con métricas online contra la baseline.

Las dos reglas que ordenan todo:

- Cada fase termina sirviendo **un post real** (la cadencia de 15 días no se frena por el build).
- Cada fase prueba **el supuesto más riesgoso que queda** (la voz fue primero; el monorepo, después).

**No es solo builds.** El sistema cubre los cuatro tipos que escribís: **builds, explainers, bridge y field-notes** (taxonomía confirmada en el plan). Los builds son el **caso más difícil y el test case**, porque necesitan que Nova lea el repo (fase 4); los explainers van a Nova sin esa herramienta, con URLs y docs como fuente; bridge y field-notes salen con lo mismo que ya funciona hoy. El resto del flujo es idéntico para los cuatro: misma voz, mismo Brown, mismo gate, mismo borrador a Substack.

Contexto y alcance completo: `~/Documents/TheUnderdoc/capstone-plan.md` (rev 2). Memoria: Engram `course/capstone-plan` (#35) y `capstone/s1-1-hardening-design` (#45).
