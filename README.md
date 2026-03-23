# 📖 VAILIB: The Ultimate Digital Library 🚀

[![GitHub License](https://img.shields.io/github/license/vikgr/vailib)](https://github.com/vikgr/vailib/blob/main/LICENSE)
[![Docker Image](https://img.shields.io/docker/pulls/zveronline/vailib)](https://hub.docker.com/r/zveronline/vailib)

**Vailib** (v3.5) is a high-performance, modernized digital library ecosystem. It combines a powerful **Telegram Document Converter Bot** with a gorgeous, responsive **Web OPDS Catalog** engine. 

Built for book lovers, researchers, and archival enthusiasts, Vailib transforms a raw collection of files into a premium, searchable, and globally accessible library experience.

> [!NOTE]
> **Vailib** is built on the robust foundation of the [SOPDS](https://github.com/zveronline/sopds) project by **zveronline**. We have extended the core engine with a completely new UI, deep internationalization, and integrated document processing pipelines.

---

## 🌟 Key Features

### 🎨 Dual-Identity UI Engine
Vailib features a revolutionary theme engine that adapts to any device:
- **Premium Dark Mode**: A sleek, modern "Cyber-Cat" interface with vibrant accents, CSS transitions, and an OLED-optimized layout. 
- **High-Efficiency E-Ink Mode**: A pure 1-bit, high-contrast, zero-animation interface specifically engineered for Kindle, Remarkable, and older e-readers.

### 🌎 Global Language Matrix (10+1)
The entire library interface—including dynamic breadcrumbs and system messages—is fully translated into the world's most popular languages:
- 🇬🇧 English | 🇷🇺 Russian | 🇩🇪 German | 🇬🇷 Greek | 🇪🇸 Spanish | 🇫🇷 French
- 🇸🇦 Arabic | 🇮🇳 Hindi | 🇵🇹 Portuguese | 🇨🇳 Chinese (Simplified)

### 🤖 Automatic Document Pipeline
Integrated **Telegram Converter Bot** support:
- Upload any **PDF** or **DJVU** via Telegram.
- **OCR Integration**: Automatically performs OCR on image-only documents.
- **Auto-Cataloging**: Converted documents are instantly saved to the library volume and indexed for the web catalog.

### ⚡ Docker-First Deployment
Vailib is shipped as a unified, zero-configuration Docker container. No more complex volume bind-mounts for UI customization—everything is compiled natively into the source.

---

## 🚀 Getting Started

Build and run your own Vailib server in minutes:

### 1. Clone the Repository
```bash
git clone https://github.com/vikgr/vailib.git
cd vailib
```

### 2. Build the Docker Image
Navigate to the [docker](./docker) directory for detailed build instructions:
```bash
cd docker
docker build -t vailib:latest .
```

### 3. Launch with Docker Compose
```yaml
version: '3.7'
services:
  vailib:
    image: vailib:latest
    container_name: vailib
    ports:
      - "8001:8001"
    volumes:
      - /your/library/path:/var/www/html/books:ro
      - vailib_db:/var/lib/mysql
volumes:
  vailib_db:
```

---

## 📁 Project Structure

- `/docker`: Dockerfiles and native image build logic. No more messy server-side binds.
- `/vailib/templates`: Overhauled Django templates featuring the "Vailib" UI identity.
- `/vailib/static/custom`: Centralized CSS/JS for the Modern and E-Ink theme engines.
- `views.py` & `models.py`: Enhanced backend logic for breadcrumb translation and cover processing.

---

## 🤝 Contributing
Vailib is an open-source project. Contributions, bug reports, and feature requests are welcome!

**GitHub Repository**: [https://github.com/vikgr/vailib](https://github.com/vikgr/vailib)

---

## ⚖️ Credits & License
Vailib is licensed under the GPL-3.0 License.

**Foundation**: Based on [SOPDS](https://github.com/zveronline/sopds) by **zveronline**.
**Development**: Engineered by **vikgr**.
