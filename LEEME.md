# Noticiero (instalación, una sola vez)

1. Crear una cuenta gratuita en github.com y un repositorio nuevo, **público**, por ejemplo `noticiero`.
2. Subir todo el contenido de esta carpeta al repositorio (incluida la carpeta oculta `.github`).
3. En el repositorio: Settings > Actions > General > Workflow permissions > "Read and write permissions" > Save.
4. Pestaña Actions > "Actualizar noticias" > Run workflow. Esperar a que termine (aparece news.json en el repositorio).
5. Settings > Pages > Source: "Deploy from a branch" > Branch: main, carpeta / (root) > Save.
6. La web queda en https://TU-USUARIO.github.io/noticiero/ y se actualiza sola cada 30 minutos.

Para cambiar medios o categorías, editar feeds.json. Si un medio falla, el registro de la ejecución en Actions indica cuál.
