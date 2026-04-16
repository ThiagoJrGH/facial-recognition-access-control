# 🔐 Sistema de Control de Acceso con Reconocimiento Facial

Sistema desarrollado como proyecto académico enfocado en la **gestión de accesos mediante reconocimiento facial**, integrando autenticación, almacenamiento de datos y una interfaz web administrativa.

El objetivo no es solo funcionalidad, sino demostrar **capacidad de diseño e integración de componentes reales**: visión por computadora, backend en Python y una interfaz web básica.

## 🚀 Resumen del Proyecto

Aplicación que permite:

- Registrar usuarios autorizados mediante imágenes faciales  
- Verificar accesos en tiempo real utilizando reconocimiento facial  
- Gestionar usuarios y eventos desde una interfaz web  
- Notificar eventos mediante correo electrónico  

El sistema está diseñado como una solución modular, donde cada componente cumple una responsabilidad específica.

## 🧠 Características Principales

### 🔐 Control de Acceso
- Verificación de identidad mediante reconocimiento facial  
- Sistema de autenticación con roles (admin / usuario)  
- Registro de accesos y validación de usuarios autorizados  

### 🧬 Reconocimiento Facial
- Comparación de rostros basada en similitud  
- Umbral configurable para validación (`similarity_threshold`)  
- Gestión de dataset local de rostros autorizados  

### 🌐 Interfaz Web Administrativa
- Panel web (`web_admin/`) para gestión básica  
- Visualización de usuarios y control del sistema  
- Integración directa con el backend en Python  

### 📧 Notificaciones
- Envío de correos ante eventos relevantes  
- Configuración SMTP integrada  

## 🛠️ Stack Tecnológico

- **Backend:** Python  
- **Base de Datos:** MySQL  
- **Visión por Computadora:** OpenCV / face recognition  
- **Frontend:** HTML (panel administrativo)  
- **Integraciones:** SMTP (notificaciones por correo)

## 🏗️ Arquitectura del Sistema

```bash
reconocimiento-facial/
│
├── clases/                
│   ├── auth_system.py     
│   ├── database.py        
│   ├── reconocimiento_fac.py  
│   ├── web_server.py      
│   ├── email_envio.py     
│   └── voice.py           
│
├── web_admin/             
│   └── index.html
│
├── main.py                
├── config.py.example      
├── scriptmysql.sql        
└── MANUAL DE USUARIO.pdf  