from configparser import Error
import getpass
from datetime import datetime
import cv2
import numpy as np
import os
import config

class AuthSystem:
    def __init__(self, database_manager, facial_recognition, email_sender):
        self.db = database_manager
        self.face_recognition = facial_recognition
        self.email_sender = email_sender
        self.current_user = None
        self.current_role = None
        self.current_user_id = None
    
    def login(self):
        """Sistema de login principal"""
        print("\n🔐 SISTEMA DE AUTENTICACIÓN")
        print("=" * 40)
        print("1. 👤 Login como Usuario")
        print("2. 📝 Registrar nuevo usuario")
        print("3. 🔧 Login como Administrador")
        print("4. 🚪 Salir")
        
        try:
            choice = input("Seleccione opción: ").strip()
            
            if choice == "1":
                return self.user_login()
            elif choice == "2":
                success = self.register_new_user()
                if success:
                    # Si el registro fue exitoso, mostrar menú de usuario automáticamente
                    self.show_user_menu()
                return False
            elif choice == "3":
                return self.admin_login()
            elif choice == "4":
                return False
            else:
                print("❌ Opción no válida")
                return self.login()
                
        except KeyboardInterrupt:
            print("\n🛑 Operación cancelada")
            return False
    
    def register_new_user(self):
        """Registra un nuevo usuario en el sistema y registra su rostro automáticamente"""
        print("\n📝 REGISTRO DE NUEVO USUARIO")
        print("=" * 35)
        
        username = input("Ingrese el nombre de usuario: ").strip()
        
        if not username:
            print("❌ El nombre de usuario no puede estar vacío")
            return False
        
        password = getpass.getpass("Ingrese la contraseña: ").strip()
        confirm_password = getpass.getpass("Confirme la contraseña: ").strip()
        
        if not password:
            print("❌ La contraseña no puede estar vacía")
            return False
        
        if password != confirm_password:
            print("❌ Las contraseñas no coinciden")
            return False
        
        # Registrar usuario en la base de datos
        success, message = self.db.register_new_user(username, password)
        
        if success:
            print(f"✅ {message}")
            
            # Configurar el usuario actual
            self.current_user = username
            self.current_role = 'user'
            
            # Obtener el ID del usuario
            self.current_user_id = self.db.get_user_id(username)
            
            # Registrar rostro automáticamente
            print("\n📷 Ahora vamos a registrar su rostro...")
            face_registered = self.register_new_face_automatic()
            
            if face_registered:
                print("🎉 ¡Registro completado exitosamente!")
                print("🤖 Redirigiendo al menú principal...")
                return True
            else:
                print("⚠️  Usuario registrado, pero no se pudo completar el registro facial.")
                print("Puede registrar su rostro más tarde desde el menú de usuario.")
                return True
        else:
            print(f"❌ {message}")
            return False
    
    def _check_duplicate_face(self, frame, current_username):
        """Verifica si el rostro capturado ya está registrado para otro usuario"""
        features = self.face_recognition.extract_advanced_features(frame)
        if features is None:
            return None, None  # No se detectó rostro
        
        threshold = config.SYSTEM_CONFIG['similarity_threshold']
        
        for name, user_data in self.face_recognition.known_faces.items():
            # Ignorar al usuario actual (permite actualizar su propio rostro)
            if name.lower() == current_username.lower():
                continue
            
            similarity = self.face_recognition.compare_faces(features, user_data['features'])
            if similarity > threshold:
                return name, similarity  # Rostro duplicado encontrado
        
        return None, None  # No hay duplicados

    def register_new_face_automatic(self):
        """Registra el rostro automáticamente después del registro"""
        if not self.current_user:
            return False
        
        print(f"\n📷 Registrando rostro para: {self.current_user}")
        print("Mire a la cámara y presione ESPACIO para capturar")
        print("Presione Q para cancelar el registro facial")
        
        frame = self.face_recognition.capture_face()
        if frame is None:
            print("❌ No se pudo capturar el rostro")
            return False
        
        # Verificar si el rostro ya está registrado para otro usuario
        duplicate_user, similarity = self._check_duplicate_face(frame, self.current_user)
        if duplicate_user:
            print(f"❌ Este rostro ya está registrado para el usuario '{duplicate_user}' (similitud: {similarity:.3f})")
            print("⚠️  No se puede usar el mismo rostro para múltiples usuarios.")
            return False
        
        # Guardar la imagen en la carpeta de usuarios autorizados
        faces_dir = config.SYSTEM_CONFIG['known_faces_dir']
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
        
        # Generar nombre de archivo
        filename = f"{self.current_user}.jpg"
        filepath = os.path.join(faces_dir, filename)
        
        # Guardar imagen
        success = cv2.imwrite(filepath, frame)
        
        if not success:
            print("❌ Error guardando la imagen del rostro")
            return False
        
        # Actualizar known_faces
        features = self.face_recognition.extract_advanced_features(frame)
        if features is not None:
            self.face_recognition.known_faces[self.current_user] = {
                'path': filepath,
                'features': features
            }
            print(f"✅ Rostro registrado exitosamente para {self.current_user}")
            return True
        else:
            print("❌ No se pudieron extraer características del rostro")
            # Eliminar la imagen si no se pudieron extraer características
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    
    def user_login(self):
        """Login para usuarios normales"""
        print("\n👤 LOGIN DE USUARIO")
        print("=" * 30)
        
        print("1. 🔍 Login por Reconocimiento Facial")
        print("2. 🔑 Login por Usuario y Contraseña")
        print("3. 🔙 Volver")
        
        try:
            choice = input("Seleccione opción: ").strip()
            
            if choice == "1":
                success = self.facial_login()
                if success:
                    self.show_user_menu()
                return success
            elif choice == "2":
                success = self.password_login_user()
                if success:
                    self.show_user_menu()
                return success
            elif choice == "3":
                return self.login()
            else:
                print("❌ Opción no válida")
                return self.user_login()
                
        except KeyboardInterrupt:
            print("\n🛑 Operación cancelada")
            return False

    def facial_login(self):
        """Login mediante reconocimiento facial"""
        print("\n📷 Login por Reconocimiento Facial")
        print("Mire a la cámara para identificarse...")
        
        frame = self.face_recognition.capture_face()
        if frame is None:
            return False
        
        # Reconocer usuario
        best_match, similarity = self.face_recognition.recognize_face(frame)
        
        if similarity > config.SYSTEM_CONFIG['similarity_threshold']:
            print(f"✅ ¡Bienvenido {best_match}!")
            
            # Verificar que el usuario existe en la base de datos
            user_id = self.db.get_user_id(best_match)
            if user_id:
                self.current_user = best_match
                self.current_user_id = user_id
                self.current_role = 'user'
                return True
            else:
                print("❌ Usuario no encontrado en la base de datos. Por favor regístrese primero.")
                return False
        else:
            print("❌ Usuario no reconocido. Por favor regístrese primero.")
            return False

    def password_login_user(self):
        """Login por usuario y contraseña"""
        print("\n🔑 Login por Usuario y Contraseña")
        username = input("Ingrese su nombre de usuario: ").strip()
        password = getpass.getpass("Ingrese su contraseña: ").strip()
        
        if not username or not password:
            print("❌ Usuario y contraseña son requeridos")
            return False
        
        # Verificar credenciales en la base de datos
        success, user_data = self.db.verify_user_credentials(username, password)
        
        if success and user_data:
            self.current_user = user_data['nombre']
            self.current_user_id = user_data['id']
            self.current_role = user_data['rol']
            print(f"✅ ¡Bienvenido {self.current_user}!")
            return True
        else:
            print("❌ Credenciales incorrectas o usuario no existe")
            return False

    def admin_login(self):
        """Login para administradores"""
        print("\n🔧 LOGIN DE ADMINISTRADOR")
        username = input("Ingrese el usuario administrador: ").strip()
        password = getpass.getpass("Ingrese la contraseña de administrador: ").strip()
        
        # Verificar credenciales de administrador
        success, user_data = self.db.verify_user_credentials(username, password)
        
        if success and user_data and user_data['rol'] == 'admin':
            self.current_user = user_data['nombre']
            self.current_user_id = user_data['id']
            self.current_role = 'admin'
            print("✅ ¡Acceso de administrador concedido!")
            return True
        else:
            print("❌ Credenciales de administrador incorrectas")
            return False

    def has_permission(self, permission):
        """Verifica si el usuario actual tiene un permiso específico"""
        if self.current_role and permission in config.ROLES_CONFIG[self.current_role]['permissions']:
            return True
        return False

    def show_user_menu(self):
        """Muestra el menú para usuarios normales con opciones mejoradas"""
        while True:
            print(f"\n🎯 MENÚ DE USUARIO - 👤 {self.current_user}")
            print("=" * 50)
            print("1. 📷 Registrar/Actualizar mi rostro")
            print("2. 🔐 Verificar acceso ")
            print("3. 📋 Ver mi historial de accesos")
            print("4. 🔓 Cerrar sesión")
            
            try:
                choice = input("Seleccione opción: ").strip()
                
                if choice == "1":
                    self.register_new_face()
                elif choice == "2":
                    self.verify_access()  
                elif choice == "3":
                    self.view_own_history()
                elif choice == "4":
                    print("👋 Sesión cerrada")
                    self.current_user = None
                    self.current_user_id = None
                    self.current_role = None
                    break
                else:
                    print("❌ Opción no válida")
                    
            except KeyboardInterrupt:
                print("\n🛑 Operación cancelada")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def show_admin_menu(self):
        """Muestra el menú para administradores - VERSIÓN SIMPLIFICADA"""
        while True:
            print(f"\n🎯 MENÚ DE ADMINISTRADOR - 🔧 {self.current_user}")
            print("=" * 50)
            print("1. 🌐 Panel Web de Administración")
            print("2. 👥 Ver usuarios registrados")
            print("3. 🔍 Buscar accesos por voz")
            print("4. 🔓 Cerrar sesión")
            
            try:
                choice = input("Seleccione opción: ").strip()
                
                if choice == "1":
                    return 'admin_panel'
                elif choice == "2":
                    return 'view_users'
                elif choice == "3":
                    return 'voice_search'
                elif choice == "4":
                    print("👋 Sesión de administrador cerrada")
                    self.current_user = None
                    self.current_user_id = None
                    self.current_role = None
                    return 'logout'
                else:
                    print("❌ Opción no válida")
                    
            except KeyboardInterrupt:
                print("\n🛑 Operación cancelada")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def manage_users(self):
        """Gestión de usuarios para administradores"""
        print("\n👤 GESTIÓN DE USUARIOS")
        print("=" * 30)
        
        users = self.db.get_all_users()
        
        if not users:
            print("No hay usuarios registrados")
            return
        
        print(f"\n{'ID':<4} {'USUARIO':<20} {'ROL':<10} {'REGISTRO':<12} {'ESTADO':<8}")
        print("-" * 65)
        
        for user in users:
            estado = "🟢 Activo" if user['activo'] else "🔴 Inactivo"
            fecha_reg = user['fecha_registro'].strftime('%d/%m/%Y') if user['fecha_registro'] else 'N/A'
            print(f"{user['id']:<4} {user['nombre']:<20} {user['rol']:<10} {fecha_reg:<12} {estado:<8}")
        
        print("\n1. 🔄 Activar/Desactivar usuario")
        print("2. 🔙 Volver")
        
        choice = input("Seleccione opción: ").strip()
        
        if choice == "1":
            self.toggle_user_status(users)
        elif choice == "2":
            return
        else:
            print("❌ Opción no válida")

    def toggle_user_status(self, users):
        """Activa o desactiva un usuario"""
        try:
            user_id = int(input("Ingrese el ID del usuario: ").strip())
            
            # Encontrar el usuario
            user = next((u for u in users if u['id'] == user_id), None)
            
            if not user:
                print("❌ ID de usuario no válido")
                return
            
            nuevo_estado = not user['activo']
            estado_str = "activado" if nuevo_estado else "desactivado"
            
            conn = self.db.get_connection()
            if not conn:
                print("❌ Error de conexión a la base de datos")
                return
            
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE usuarios SET activo = %s WHERE id = %s",
                    (nuevo_estado, user_id)
                )
                conn.commit()
                print(f"✅ Usuario {user['nombre']} {estado_str} correctamente")
            
            except Error as e:
                print(f"❌ Error actualizando usuario: {e}")
            finally:
                if conn and conn.is_connected():
                    conn.close()
                    
        except ValueError:
            print("❌ Por favor ingrese un ID válido")

    def register_new_face(self):
        """Registra un nuevo rostro para el usuario actual"""
        if not self.current_user:
            print("❌ No hay usuario logueado")
            return
        
        print(f"\n📷 Registrando rostro para: {self.current_user}")
        print("Mire a la cámara y presione ESPACIO para capturar")
        
        frame = self.face_recognition.capture_face()
        if frame is None:
            return
        
        # Verificar si el rostro ya está registrado para otro usuario
        duplicate_user, similarity = self._check_duplicate_face(frame, self.current_user)
        if duplicate_user:
            print(f"❌ Este rostro ya está registrado para el usuario '{duplicate_user}' (similitud: {similarity:.3f})")
            print("⚠️  No se puede usar el mismo rostro para múltiples usuarios.")
            return
        
        # Guardar la imagen en la carpeta de usuarios autorizados
        faces_dir = config.SYSTEM_CONFIG['known_faces_dir']
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
        
        # Generar nombre de archivo
        filename = f"{self.current_user}.jpg"
        filepath = os.path.join(faces_dir, filename)
        
        # Guardar imagen
        cv2.imwrite(filepath, frame)
        
        # Actualizar known_faces
        self.face_recognition.known_faces[self.current_user] = {
            'path': filepath,
            'features': self.face_recognition.extract_advanced_features(frame)
        }
        
        print(f"✅ Rostro registrado exitosamente para {self.current_user}")

    def verify_access(self):
        """Verifica el acceso del usuario actual y envía email"""
        if not self.current_user:
            print("❌ No hay usuario logueado")
            return
        
        print(f"\n🔐 Verificando acceso para: {self.current_user}")
        print("Mire a la cámara para verificar su identidad...")
        
        frame = self.face_recognition.capture_face()
        if frame is None:
            return
        
        # Verificar si coincide con el usuario actual
        best_match, similarity = self.face_recognition.recognize_face(frame)
        
        if best_match == self.current_user and similarity > config.SYSTEM_CONFIG['similarity_threshold']:
            print(f"✅ ¡Acceso verificado! Coincidencia: {similarity:.3f}")
            
            # Enviar email de verificación exitosa
            print("📧 Enviando notificación por email...")
            email_success = self.email_sender.send_detailed_email(
                frame, 
                self.current_user, 
                "PERMITIDO", 
                similarity
            )
            
            if email_success:
                print("✅ Email enviado correctamente")
            else:
                print("❌ Error enviando email")
                
        else:
            print(f"❌ Verificación fallida. Usuario detectado: {best_match}, Similitud: {similarity:.3f}")
            
            # También enviar email para acceso denegado
            print("📧 Enviando notificación por email...")
            email_success = self.email_sender.send_detailed_email(
                frame, 
                f"Intento de acceso como {best_match}", 
                "DENEGADO", 
                similarity
            )
            
            if email_success:
                print("✅ Email enviado correctamente")
            else:
                print("❌ Error enviando email")

    def view_own_history(self):
        """Muestra el historial de accesos del usuario actual"""
        if not self.current_user:
            print("❌ No hay usuario logueado")
            return
        
        print(f"\n📋 HISTORIAL DE ACCESOS DE: {self.current_user}")
        print("=" * 60)
        
        history = self.db.get_user_access_history(self.current_user)
        
        if not history:
            print("No se encontraron accesos para este usuario")
            return
        
        # Mostrar en formato tabla
        print(f"{'FECHA/HORA':<20} {'TIPO':<12} {'SIMILITUD':<10}")
        print("-" * 50)
        
        for acceso in history:
            tipo_acceso = acceso[0]
            fecha = acceso[1]
            similitud = acceso[2]
            
            if hasattr(similitud, 'item'):
                similitud = similitud.item()
            
            fecha_str = fecha.strftime('%d/%m/%Y %H:%M') if fecha else 'N/A'
            similitud_str = f"{similitud:.3f}" if similitud else 'N/A'
            
            print(f"{fecha_str:<20} {tipo_acceso:<12} {similitud_str:<10}")
        
        # Mostrar estadísticas
        total_accesos = len(history)
        accesos_permitidos = sum(1 for acceso in history if acceso[0] == 'PERMITIDO')
        porcentaje_exito = (accesos_permitidos / total_accesos * 100) if total_accesos > 0 else 0
        
        print("\n📊 ESTADÍSTICAS:")
        print(f"   Total de accesos: {total_accesos}")
        print(f"   Accesos permitidos: {accesos_permitidos}")
        print(f"   Porcentaje de éxito: {porcentaje_exito:.1f}%")

    def _process_user_search(self, username):
        """Procesa la búsqueda del usuario (método auxiliar para voice_search)"""
        if not username:
            return
            
        conn = self.db.get_connection()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nombre FROM usuarios 
                WHERE LOWER(nombre) LIKE %s
                ORDER BY nombre
            """, (f"%{username}%",))
            
            matches = cursor.fetchall()
            
            if not matches:
                print(f"❌ No se encontraron usuarios que coincidan con '{username}'")
                return
                
            if len(matches) == 1:
                selected_user = matches[0][0]
                print(f"✅ Usuario encontrado: {selected_user}")
            else:
                print("\n🔍 Múltiples usuarios encontrados:")
                for i, (match,) in enumerate(matches, 1):
                    print(f"{i}. {match}")
                
                try:
                    selection = int(input("Seleccione el número del usuario: ")) - 1
                    if 0 <= selection < len(matches):
                        selected_user = matches[selection][0]
                    else:
                        print("❌ Selección inválida")
                        return
                except ValueError:
                    print("❌ Por favor ingrese un número válido")
                    return
            
            # Mostrar historial
            print(f"\n📋 HISTORIAL DE ACCESOS DE: {selected_user}")
            print("-" * 50)
            
            cursor.execute("""
                SELECT tipo_acceso, fecha_acceso, similitud
                FROM accesos 
                WHERE nombre_usuario = %s
                ORDER BY fecha_acceso DESC
            """, (selected_user,))
            
            resultados = cursor.fetchall()
            
            if resultados:
                for resultado in resultados:
                    similitud = resultado[2]
                    if hasattr(similitud, 'item'):
                        similitud = similitud.item()
                    print(f"{resultado[1]} | {resultado[0]} | Similitud: {similitud or 'N/A'}")
            else:
                print("No se encontraron accesos para este usuario")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()