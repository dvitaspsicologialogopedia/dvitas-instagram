# Guía de publicación diaria · DVITAS Psicología y Logopedia (Málaga)

Este repositorio es **público**: aquí solo van imágenes y vídeos que se van a publicar en redes. Nunca datos de pacientes.

## Objetivo
Contenido que se **guarde, se comparta y genere conversación**, y que lleve a las familias a pedir cita. Rigor clínico siempre (DSM-5-TR, CIE-11 traducidos a lenguaje familiar). Nada de clickbait ni sensacionalismo de salud.

## Ritmo
| Día | Feed | Stories | Reel |
|---|---|---|---|
| Todos los días | Carrusel A (azul, eje del día) 13:30 + Carrusel B (crema, actualidad) 18:00 | Del A | Del B, 20:30 |

- Carruseles: Instagram, Facebook, TikTok (fotos) y Google Business (publicación con la primera imagen).
- Stories: portada y CTA del carrusel **azul** (dos stories, 13:35 y 19:00). Los crema no van a stories.
- Reels (del crema): Instagram, TikTok y Facebook Reel. Sin música. YouTube aún no está conectado.

## Ejes del carrusel A (azul) por día (rotar el subtema; mirar `historial.md` para no repetir en 4 semanas)
| Día | Eje | Subtemas |
|---|---|---|
| Lunes | EVALUACIÓN NEUROPSICOLÓGICA | Cuándo evaluar, qué incluye, mitos de los tests, TDAH más allá de la hiperactividad, dislexia, altas capacidades |
| Martes | PSICOLOGÍA INFANTIL | Miedos, rabietas, adaptación al colegio, señales de alerta emocional, celos entre hermanos |
| Miércoles | Semanas alternas: LOGOPEDIA INFANTIL / LOGOPEDIA DE ADULTOS | Infantil: señales de alerta por edad, juegos para estimular el habla, pronunciación (r, l), "ya hablará", tartamudez infantil. Adultos: afasia tras ictus, disfonía, tartamudez adulta, rehabilitación cognitiva |
| Jueves | FAMILIA | Rutinas, deberes, comunicación en casa, pantallas, preparar una evaluación |
| Viernes | TRASTORNOS DEL SUEÑO | Rutina de sueño, despertares, ronquidos, cuándo consultar (con la Dra. Fernández Fígares) |
| Sábado | PAREJAS (única pieza de parejas de la semana) | Discutir bien, comunicación, estrés y convivencia, crianza en pareja, celos, reparar tras una discusión |
| Domingo | PSICOLOGÍA DE ADULTOS | Ansiedad, estrés y agotamiento, duelo, autoestima, insomnio y rumiación, cuándo pedir ayuda |

## Carrusel B (crema) · ACTUALIDAD, todos los días, con Reel
Eje de la píldora: "ACTUALIDAD"; tema: 1–3 palabras de la noticia (p. ej. "PANTALLAS Y SUEÑO").
Busca con WebSearch noticias y tendencias de los **últimos 7 días** (España primero, luego internacional).

**Parámetros para elegir (debe cumplirlos todos):**
1. Fuente fiable: medio general serio, Ministerio de Sanidad o Educación, OMS, sociedades científicas, universidad o estudio publicado (PubMed). Nunca solo redes sociales.
2. Relación clara con nuestras áreas: salud mental, sueño, lenguaje y comunicación, neurodesarrollo (TDAH, dislexia, TEA), educación y colegio, familia y crianza, pantallas y tecnología, mayores y deterioro cognitivo.
3. Se puede convertir en algo práctico para una familia o un adulto ("qué significa para ti" + "qué puedes hacer").
4. Interesa a mucha gente (aparece en varios medios o es tendencia).

**Excluir siempre:** sucesos trágicos o casos con personas identificables (sobre todo menores), noticias de suicidio salvo para dar recursos de ayuda, política partidista o temas polarizados, "estudios milagro" sin respaldo, alarmismo.

**Si ningún tema cumple:** usa una tendencia de temporada o del calendario (exámenes, Navidad y pantallas, cambio de hora, vuelta al cole, días mundiales de salud).

**Estructura del B:** portada con gancho de actualidad · "Qué ha pasado" (2–3 frases, sin exagerar) · "Qué significa" (lectura clínica sencilla) · "Qué puedes hacer" (pasos) · CTA. En el caption, al final: "Fuente: <medio o entidad, fecha>". No repetir noticias de `historial.md`. No usar fotos de prensa ni logos de medios.

El eje de la píldora es la **categoría real** de la pieza: MITOS VS REALIDAD, BAMBALINAS o DIVERTRAINING sustituyen al eje del día cuando la pieza es de ese tipo. Proporción mensual aproximada: 40 % educación clínica · 25 % tips para familias · 15 % bambalinas · 10 % mitos · 10 % DIVERTRAINING. Series en el carrusel A: "Lo que dice la evidencia" (lunes), "Mito de la semana" (jueves, con eje MITOS VS REALIDAD), "3 señales…" (viernes). En adultos y parejas, mismo rigor: nada de diagnósticos a distancia; derivar a cita.

## Estructura de cada carrusel (5–7 slides)
1. `portada`: gancho de **máximo 8 palabras** (pregunta que genera duda, afirmación que sorprende, cifra o lista, contraste) + subtítulo corto.
2. Slides 2–5: una idea por slide (`lista` con 3–5 viñetas, `pasos`, `datos`).
3. Penúltima: "Lo que sí puedes hacer hoy" (valor inmediato), normalmente `pasos`.
4. Última: `cta` o `cierre`.
- Lista de señales: siempre `"aviso": true` (aviso clínico).
- `datos` solo con cifras orientativas bien establecidas y fuente oficial citada en el caption; ante la duda, no uses `datos`.
- Titulares de slide de máximo 3 líneas; frases cortas. Sin emojis en las imágenes.

## Ficha `spec.json` (la lee `tools/render.py`)
```json
{"fondo": "azul", "eje": "PSICOLOGÍA INFANTIL", "tema": "MIEDOS", "reel": false,
 "slides": [
  {"tipo": "portada", "titulo": "¿Miedo normal o señal de alerta?", "subtitulo": "Cómo distinguirlos"},
  {"tipo": "lista", "titulo": "Cuándo conviene consultar", "items": ["...", "..."], "aviso": true},
  {"tipo": "pasos", "titulo": "Qué puedes hacer hoy", "pasos": [["Valida el miedo", "No lo minimices."]]},
  {"tipo": "datos", "titulo": "...", "filas": [["18 meses", 0.3, "20-50 palabras"]], "nota": "Orientativo. Fuente: ..."},
  {"tipo": "cta", "titulo": "Guárdalo y envíaselo a quien lo necesite"}
 ]}
```
`fondo`: "azul" (carrusel A) o "crema" (carrusel B). `reel: true` solo en el crema. `tema`: 1–3 palabras.

## Caption
- Primera línea = gancho. 4–8 líneas claras, lenguaje cercano y riguroso.
- Una línea "Guárdalo para…" o "Envíaselo a…".
- CTA: "Pide cita en DVITAS (Málaga): enlace en la bio o WhatsApp 744 646 732."
- 8–12 hashtags mezclando marca (#dvitas #dvitaspsicologia), pilar (#psicologiainfantil #logopedia #neuropsicologia…) y localización (#malaga #psicologiamalaga #logopedamalaga). Rotar.
- Si hay datos de terceros: "Fuente: …" al final.

## Límites (obligatorios)
- Nunca diagnosticar a distancia ni prometer resultados ("curar", "garantizado", "100 %").
- Nunca datos identificables de pacientes ni casos reales sin consentimiento.
- Sin música en los Reels. Sin Canva.
