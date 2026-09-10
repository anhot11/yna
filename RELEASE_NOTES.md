## 🍑 yna v2.0.0 — Anatomía Femenina y Piel Hiperrealista

Esta actualización mayor transforma por completo el modelo corporal femenino, el sombreado cutáneo y la fidelidad física en tiempo real.

### ✨ Novedades Principales

- **Modelado y Esculpido Anatómico Realista (169,362 vértices)**:
  - Hendidura interglútea profunda con compresión lateral.
  - Modelado anatómico íntimo con labios mayores, vulva y surco medio.
  - Repliegues radiales y orificio anal modelado de forma natural.
  - Pliegue infraglúteo (transición glúteo-muslo) y hoyuelos lumbo-sacros de Venus.
- **Shader de Piel Orgánica (Godot 4 GLSL)**:
  - Dispersión Subsuperficial (Subsurface Scattering - SSS) dinámica con mayor vascularización dérmica en zonas íntimas (`sss_local`).
  - Gradiente térmico y variación de tono de piel anatómico (adiós al aspecto de plástico blanco).
  - Dual-lobe specular con micro-poros tangenciales y brillo cutáneo Schlick-GGX.
  - Sonrojo dérmico reactivo acumulativo con disipación térmica gradual.
- **Física de Tejido Blando Multi-Armónico**:
  - 6 osciladores armónicos con resonancia biológica y amortiguación natural.
  - Interacción táctil en tiempo real con hundimiento (*indentation*), arrastre y liberación (*snap-back*).
  - Transferencia elástica cruzada entre ambos glúteos (*inter-cheek shear coupling*).
  - Ondas de choque dinámicas propagadas por GPU (*vertex shader ripple*).
- **Lencería 3D Física con Espesor Real**:
  - Prendas modeladas con modificadores Solidify y dobladillos elásticos redondeados (*Bevel*).
  - Modos: Bikini Clásico, Tanga Sexy y Sin Ropa.
- **Soporte Móvil Nativo**:
  - Controles táctiles optimizados para Android con cambio de modo (Slap / Rotación).
  - Cámara orbital 3D con inercia y zoom elástico.
  - Menú de ajustes gráficos con 4 presets de rendimiento (Baja, Media, Alta, Ultra).

---

### 📦 Archivos Adjuntos
- **`yna-v2.0-release.apk`**: APK firmado y listo para instalar en cualquier dispositivo Android (ARM64 y ARMv7).
