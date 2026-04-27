# 🚀 Guía Fundamental: Contenedores, Docker y Podman

Este documento explica los conceptos clave de la tecnología de contenedores que estamos utilizando en este proyecto.

## 1. ¿Qué es un Contenedor?
Imagina que quieres enviar un mueble por barco. En lugar de soltar las piezas en la cubierta, las metes en un **Contenedor de Carga**. El contenedor tiene todo lo necesario dentro y no importa en qué barco se suba, el contenido siempre llega igual.

En software, un **Contenedor** es un paquete ligero que incluye todo lo que tu aplicación necesita para ejecutarse: código, librerías (como OpenCV o PySerial), configuración y el entorno de Python.

## 2. Conceptos Clave

### 🖼️ La Imagen (El Plano)
La imagen es un archivo de "solo lectura" que contiene las instrucciones para crear un contenedor. Es como la **receta** de una tarta o los **planos** de una casa. 
- No puedes "ejecutar" una imagen, la usas para "lanzar" un contenedor.
- En este proyecto, tu imagen se define en el `Dockerfile`.

### 📦 El Contenedor (La Instancia)
Es la imagen en ejecución. Si la imagen es la receta, el contenedor es la **tarta ya cocinada**.
- Puedes tener 10 contenedores corriendo basados en la misma imagen.
- Son aislados: lo que pasa dentro de un contenedor no afecta al host (tu PC) ni a otros contenedores.

### 📜 Dockerfile (Las Instrucciones)
Es un archivo de texto con la lista de pasos para construir tu imagen. 
- Ejemplo: "Usa Python 3.12", "Instala OpenCV", "Copia mi código".

### 🎼 Docker Compose (El Director de Orquesta)
Es una herramienta para definir y correr aplicaciones de varios contenedores. En nuestro caso, lo usamos para simplificar comandos largos (como el mapeo de volúmenes y dispositivos seriales) en un solo archivo `docker-compose.yml`.

## 3. ¿Qué pasa en mi máquina? (Contenedores vs VMs)

Es vital entender que **un contenedor NO es una Máquina Virtual (VM)**.

| Característica | Máquina Virtual (VM) | Contenedor |
| :--- | :--- | :--- |
| **Sistema Operativo** | Incluye un SO completo (Gigas de tamaño) | Comparte el Kernel del host (Megas de tamaño) |
| **Rendimiento** | Lento al arrancar, consume mucha RAM | Casi instantáneo, muy ligero |
| **Aislamiento** | Total (Hardware virtualizado) | Nivel de proceso (Aislado por el Kernel) |

**En tu máquina Fedora:** 
Cuando corres el contenedor, el sistema no crea un nuevo computador virtual. Simplemente lanza tu script de Python en un "espacio aislado" donde solo puede ver las librerías que le instalaste y los archivos que tú le permitiste ver (mediante volúmenes).

## 4. El Ciclo de Vida

1.  **Build:** Tomas tu `Dockerfile` y creas una **Imagen**.
2.  **Push (Opcional):** Guardas esa imagen en la nube.
3.  **Run:** Tomas la imagen y creas un **Contenedor** vivo.

## 5. ¿Por qué usamos Podman en lugar de Docker?
En Fedora, **Podman** es la herramienta estándar. 
- **Daemon-less:** Docker necesita un proceso "jefe" (daemon) corriendo siempre como root. Podman no, lo que lo hace más seguro.
- **Rootless:** Puedes correr contenedores sin ser administrador.
- **Compatibilidad:** Casi todos los comandos de Docker funcionan en Podman.

## 6. Glosario de Términos Importantes

- **Volumen (Volumes):** Un puente entre tu carpeta real y una carpeta dentro del contenedor. Si cambias el código en tu PC, el contenedor lo ve al instante.
- **Variables de Entorno (ENV):** Configuraciones que le pasas al contenedor (como `PYTHONUNBUFFERED=1`).
- **Exponer Puertos:** Abrir una ventana para que el mundo exterior pueda hablar con tu contenedor (ej: si fuera un servidor web).
- **Z (Sufijo de volumen):** En sistemas como Fedora con SELinux, el `:Z` le dice al sistema: "Oye, deja que este contenedor toque estos archivos de mi PC de forma segura".
