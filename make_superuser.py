import os
import sys
import django

# Lisää projektin polku
sys.path.append(r'C:\Users\HP\Dev\mikrobot_django')

# Aseta oikea settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')

try:
    django.setup()
    print(" Django setup onnistui!")
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Tarkista onko käyttäjä jo olemassa
    if User.objects.filter(username='NorthFox1975').exists():
        print("ℹ Käyttäjä 'NorthFox1975' on jo olemassa!")
    else:
        # Luo superuser
        User.objects.create_superuser(
            username='NorthFox1975',
            email='markus@foxinthecode.fi', 
            password='Mummilaaksoon2025!'
        )
        print(" Superuser 'NorthFox1975' luotu onnistuneesti!")
        print("Username: NorthFox1975")
        print("Password: [määritelty]")
        
except Exception as e:
    print(f" Virhe: {e}")
    print("Kokeile: python manage.py shell")
