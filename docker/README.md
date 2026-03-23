# 🐳 VAILIB: Zero-Bind Docker Build

This directory contains the source-native build logic to transform the base [SOPDS](https://github.com/zveronline/sopds) project from **zveronline** into a fully-functional **Vailib** environment.

By building from this directory, you are natively compiling the **Vailib Premium UI**, **10-Language Translation Matrix**, and **"Cyber-Cat" Theme Engine** directly into the binary. No more messy server-side volume mounts or complex Docker Compose configurations!

---

## 🛠️ Build Instructions

From your terminal, navigate directly into this `docker/` folder and run the build command:
```bash
docker build -t vailib:latest .
```

This will automatically pull the baseline `zveronline/vailib:latest` image and perfectly overlay all of our modifications (`modern.css`, `dl.py`, `models.py`, `views.py`, and templates) natively into their respective application directories.

---

## 🚀 Optimized Launch (Docker Compose)

Because the UI is now natively embedded in the image, your `docker-compose.yml` becomes incredibly clean. You no longer need volume binds for `/tmp/vailib_custom/` scripts!

```yaml
services:
  vailib:
    image: vailib:latest
    container_name: vailib
    restart: always
    environment:
      - VAILIB_SU_NAME=admin
      - VAILIB_SU_PASS=admin
      # [Add your other database/environment variables here...]
    ports:
      - "8001:8001"
    volumes:
      - /path/to/your/books:/var/www/html/books:ro
      - vailib_opds_db:/var/lib/mysql

volumes:
  vailib_opds_db:
```

---

## 🏗️ Inside the Build Structure

- **`src/vailib_web_backend/templates/`**: The core "Vailib" UI templates. Automatically mapped to the internal Django backend.
- **`src/static/custom/`**: Pre-loaded **Modern CSS** and **Theme Assets** (e.g., `logo_color.png`).
- **`src/opds_catalog/`**: Enhanced Python logic for server-side cover generation and document parsing via `dl.py`.

---

## 🔗 Project Resources
**Main GitHub Repository**: [https://github.com/vikgr/vailib](https://github.com/vikgr/vailib)
**Documentation**: [https://github.com/vikgr/vailib/docker](https://github.com/vikgr/vailib/tree/main/docker)
