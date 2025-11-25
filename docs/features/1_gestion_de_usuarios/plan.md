# Plan de Implementación para Gestión de Usuarios

- **Funcionalidad**: 1_gestion_de_usuarios

Implementar el sistema completo de gestión de usuarios con registro, inicio de sesión y autenticación mediante JWT (JSON Web Tokens) utilizando Django REST Framework. El sistema permitirá a los usuarios registrarse, autenticarse, gestionar su perfil y mantener sesiones seguras mediante tokens JWT.

**Nota**: Esta funcionalidad incluye tanto endpoints de API REST (`/api/users/*`) como vistas web con templates Django (`/users/*`). Ambas implementaciones comparten la misma lógica de negocio (services y repositories) pero ofrecen diferentes interfaces: JSON para API y HTML para web.

## Contexto

### Funcional
- [PRD](/docs/PRD.md)
- [DOMAIN](/docs/DOMAIN.md)
- [Issue #2](https://github.com/jsmdev/thenaturalway-backend/issues/2) - Gestión de Usuarios - Sistema de registro e inicio de sesión con autenticación JWT

### Técnico

**Tecnologías a utilizar:**
- Django 5.1.7+
- Django REST Framework (DRF) para API REST
- Django Templates para interfaz web
- djangorestframework-simplejwt para autenticación JWT (API)
- Django's built-in session authentication para web
- Django's built-in password hashing (PBKDF2)
- PostgreSQL (configurado en settings pero usando SQLite para desarrollo)

**Reglas a aplicar:**
- Arquitectura en capas: Views → Services → Repositories → Models
- Convenciones de nomenclatura: snake_case para funciones, PascalCase para clases
- Estructura de respuesta uniforme: `{"data": ..., "message": ..., "request": {...}}`
- Manejo de errores con excepciones de DRF
- Validación en serializadores y servicios
- Type hints en todas las funciones públicas

## Tareas del Plan de Implementación

### Capa de Configuración y Dependencias

- [ ] 1. Instalar dependencias necesarias: django-rest-framework y djangorestframework-simplejwt en requirements.txt

- [ ] 2. Configurar Django REST Framework en settings.py: añadir 'rest_framework' a INSTALLED_APPS y configurar REST_FRAMEWORK con autenticación JWT

- [ ] 3. Configurar djangorestframework-simplejwt en settings.py: añadir 'rest_framework_simplejwt' a INSTALLED_APPS, configurar SIMPLE_JWT con tiempos de expiración de tokens y tipo de token

- [ ] 4. Crear la app users: ejecutar `python manage.py startapp users apps/users` y añadir 'apps.users' a INSTALLED_APPS

### Capa de Modelos

- [ ] 5. Crear modelo User en apps/users/models.py: definir campos según el modelo de dominio (username, email, password, firstName, lastName, dateOfBirth, gender, height, weight, isActive, timestamps) usando AbstractUser o AbstractBaseUser

- [ ] 6. Configurar modelo User como usuario por defecto: añadir AUTH_USER_MODEL = 'users.User' en settings.py

- [ ] 7. Crear y ejecutar migraciones: ejecutar `python manage.py makemigrations` y `python manage.py migrate`

### Capa de Repositorios

- [ ] 8. Crear repositorio de usuarios en apps/users/repositories.py: implementar funciones get_user_by_id_repository, get_user_by_username_repository, get_user_by_email_repository, create_user_repository, update_user_repository

### Capa de Servicios

- [ ] 9. Crear servicio de registro en apps/users/services.py: implementar register_user_service que valide datos, verifique unicidad de username/email, cree usuario con password hasheado y retorne usuario creado

- [ ] 10. Crear servicio de autenticación en apps/users/services.py: implementar authenticate_user_service que valide credenciales y retorne usuario si es válido

- [ ] 11. Crear servicio de obtención de perfil en apps/users/services.py: implementar get_user_profile_service que retorne datos del usuario autenticado

- [ ] 12. Crear servicio de actualización de perfil en apps/users/services.py: implementar update_user_profile_service que valide y actualice campos permitidos del usuario

### Capa de Serializadores

- [ ] 13. Crear UserRegisterSerializer en apps/users/serializers.py: validar username, email, password y campos opcionales del modelo, incluir validación de unicidad

- [ ] 14. Crear UserLoginSerializer en apps/users/serializers.py: validar username/email y password para inicio de sesión

- [ ] 15. Crear UserProfileSerializer en apps/users/serializers.py: serializar datos del perfil del usuario (excluir password, incluir campos opcionales)

- [ ] 16. Crear UserUpdateSerializer en apps/users/serializers.py: permitir actualización de campos opcionales del perfil (firstName, lastName, dateOfBirth, gender, height, weight)

### Capa de Vistas

- [ ] 17. Crear UserRegisterAPIView en apps/users/views.py: endpoint POST /api/users/register/ que use UserRegisterSerializer y register_user_service, retorne usuario y tokens JWT

- [ ] 18. Crear UserLoginAPIView en apps/users/views.py: endpoint POST /api/users/login/ que use UserLoginSerializer y authenticate_user_service, retorne tokens JWT (access y refresh)

- [ ] 19. Crear UserLogoutAPIView en apps/users/views.py: endpoint POST /api/users/logout/ que invalide el refresh token usando TokenBlacklistView de simplejwt

- [ ] 20. Crear UserProfileAPIView en apps/users/views.py: endpoint GET /api/users/me/ que use get_user_profile_service y retorne perfil del usuario autenticado

- [ ] 21. Crear UserProfileUpdateAPIView en apps/users/views.py: endpoint PUT /api/users/me/ que use UserUpdateSerializer y update_user_profile_service para actualizar perfil

- [ ] 22. Crear UserTokenRefreshAPIView en apps/users/views.py: endpoint POST /api/users/refresh/ que use TokenRefreshView de simplejwt para refrescar access token

### Capa de URLs

- [ ] 23. Configurar URLs de la app users en apps/users/urls.py: crear router o path patterns para todos los endpoints (register, login, logout, me, refresh)

- [ ] 24. Registrar URLs de users en config/urls.py: añadir path('api/users/', include('apps.users.urls')) al urlpatterns principal

### Capa de Admin

- [ ] 25. Registrar modelo User en apps/users/admin.py: configurar UserAdmin para gestión en Django admin con campos relevantes

### Capa de Formularios Web

- [ ] 26. Crear formularios Django en apps/users/forms.py: UserRegisterForm, UserLoginForm, UserProfileUpdateForm para validación en vistas web

### Capa de Vistas Web

- [ ] 27. Crear UserRegisterView en apps/users/web_views.py: vista GET/POST para registro con template, usar UserRegisterForm y register_user_service, autenticación por sesión

- [ ] 28. Crear UserLoginView en apps/users/web_views.py: vista GET/POST para login con template, usar UserLoginForm y authenticate_user_service, crear sesión Django

- [ ] 29. Crear UserLogoutView en apps/users/web_views.py: vista POST para logout que cierre sesión Django

- [ ] 30. Crear UserProfileView en apps/users/web_views.py: vista GET/PUT para perfil con template, usar UserProfileUpdateForm y servicios de perfil

### Capa de Templates

- [ ] 31. Configurar directorio de templates en settings.py: añadir BASE_DIR / 'templates' a TEMPLATES['DIRS']

- [ ] 32. Crear template base en templates/base.html: estructura HTML base con navegación, mensajes y bloques extensibles

- [ ] 33. Crear template de registro en apps/users/templates/users/register.html: formulario de registro con validación y mensajes de error

- [ ] 34. Crear template de login en apps/users/templates/users/login.html: formulario de login con validación y mensajes de error

- [ ] 35. Crear template de perfil en apps/users/templates/users/profile.html: formulario de perfil con datos actuales y opción de actualización

### Capa de URLs Web

- [ ] 36. Crear URLs web en apps/users/urls.py: añadir rutas web (sin prefijo /api/) para register, login, logout, profile que apunten a web_views

- [ ] 37. Registrar URLs web en config/urls.py: añadir path('users/', include('apps.users.urls')) al urlpatterns principal (separado de API)

> Fin del Plan de Implementación para `1_gestion_de_usuarios`

