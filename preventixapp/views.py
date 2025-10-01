from django.shortcuts import render, redirect
from django.utils.dateformat import format as date_format
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import CustomUser
from .utils import get_forgotten_specialties
from appointments.ml_model import recommend_appointments
from appointments.models import Appointment 
import json
from .forms import ProfilePictureForm, ProfileInfoForm

User = get_user_model()

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            # Buscar el usuario por email
            user = User.objects.get(email=email)
            # Autenticar usando el username del usuario
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirige al dashboard después del login exitoso
            else:
                messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con este correo.')

    return render(request, 'login.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Solo correo electrónico
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Asegúrate de que 'home' esté definido en tus URLs
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('name', '').strip()
        age = request.POST.get('age', '')
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validaciones básicas
        if not all([name, email, phone, address, password, confirm_password]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'register.html')
        
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'register.html')
        
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'register.html')
        
        # Verificar si el email ya existe
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Este correo electrónico ya está registrado.')
            return render(request, 'register.html')
        
        # Verificar si el teléfono ya existe
        if CustomUser.objects.filter(phone_number=phone).exists():
            messages.error(request, 'Este número de teléfono ya está registrado.')
            return render(request, 'register.html')
        
        try:
            # Dividir el nombre en first_name y last_name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Calcular fecha de nacimiento aproximada si se proporciona la edad
            birth_date = None
            if age and age.isdigit():
                from datetime import date
                current_year = date.today().year
                birth_year = current_year - int(age)
                birth_date = date(birth_year, 1, 1)  # Usar 1 de enero como fecha aproximada
            
            # Crear el usuario
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone,
                direccion=address,  # Usar la dirección proporcionada
                birth_date=birth_date
            )
            
            # Autenticar y hacer login automáticamente
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {first_name}! Tu cuenta ha sido creada exitosamente.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Error al crear la cuenta. Inténtalo de nuevo.')
                return render(request, 'register.html')
                
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
            return render(request, 'register.html')

    return render(request, 'register.html')

@login_required
def dashboard(request):
    # Obtener estadísticas y especialidades olvidadas
    stats = (
        Appointment.objects
        .filter(user=request.user)
        .exclude(specialty__isnull=True)
        .exclude(specialty='')
        .values('specialty')
        .annotate(count=Count('specialty'))
        .order_by('-count')
    )

    labels = [item['specialty'] for item in stats]
    counts = [item['count'] for item in stats]

    forgotten = get_forgotten_specialties(request.user)
    for item in forgotten:
        item['last_date'] = date_format(item['last_date'], 'Y-m-d')

    # Obtener citas recomendadas para el usuario
    recommended_appointments = recommend_appointments(request.user.id)

    # Verificar si el DataFrame tiene datos antes de pasarlo al template
    if not recommended_appointments.empty:
        recommended_appointments = recommended_appointments.to_dict('records')
    else:
        recommended_appointments = []

    return render(request, 'dashboard.html', {
        'labels': json.dumps(labels),
        'counts': json.dumps(counts),
        'forgotten_specialties': forgotten,
        'recommended_appointments': recommended_appointments,
    })


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfilePictureForm, ProfileInfoForm

@login_required
def profile_view(request):
    user = request.user

    picture_form = ProfilePictureForm(instance=user)
    info_form = ProfileInfoForm(instance=user)

    if request.method == 'POST':
        # Actualización de la foto de perfil
        if 'save_picture' in request.POST:
            picture_form = ProfilePictureForm(request.POST, request.FILES, instance=user)

            if picture_form.is_valid():
                picture_form.save()
                messages.success(request, 'Foto de perfil actualizada correctamente.')
                return redirect('profile')
            else:
                messages.error(request, 'Hubo un problema al actualizar la foto de perfil.')

        # Actualización de información del usuario
        elif 'save_info' in request.POST:
            info_form = ProfileInfoForm(request.POST, instance=user)

            # 🔍 Verificar datos recibidos
            print("Datos recibidos en el formulario:")
            for key, value in request.POST.items():
                print(f"{key}: {value}")

            if info_form.is_valid():
                print("Formulario válido, guardando información...")
                info_form.save()
                messages.success(request, 'Información actualizada correctamente.')
                return redirect('profile')
            else:
                # 🔍 Mostrar errores si hay problemas
                print("Errores en el formulario:", info_form.errors)
                messages.error(request, 'Hubo un problema al actualizar la información.')
        else:
            picture_form = ProfilePictureForm(instance=user)
            info_form = ProfileInfoForm(instance=user)

    # 🔍 Siempre retornamos los formularios inicializados
    return render(request, 'profile.html', {
        'picture_form': picture_form,
        'info_form': info_form,
    })


