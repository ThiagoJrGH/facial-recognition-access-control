# Configuración centralizada del sistema
import os

# Configuración de Base de Datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'facial_recognition_db'
}

# Configuración de Email
EMAIL_CONFIG = {
    'sender_email': "thiagojrgc@gmail.com",
    'sender_password': "shox flvh zlie cpen", 
    'receiver_email': "thiagojrgc@gmail.com",
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

# Configuración del Sistema
SYSTEM_CONFIG = {
    'known_faces_dir': "usuarios_autorizados",
    'similarity_threshold': 0.6,
    'web_server_port': 8000,
    'admin_password': "1234"
}

# Configuración de Roles y Usuarios
ROLES_CONFIG = {
    'admin': {
        'password': '1234',
        'permissions': ['admin_panel', 'view_all_users', 'voice_search', 'view_all_access_history', 'manage_users']
    },
    'user': {
        'permissions': ['register_face', 'verify_access', 'view_own_history']
    }
}