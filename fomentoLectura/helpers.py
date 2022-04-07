
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings




def send_register_new_user(first_name,last_name,email,username):
    try:
        subject="Administración"
        message= "Estimado/a Sr./Srta.  {} {} con la dirección {}, se le notifica que su cuenta fue creado con éxito. \n\n Su usuario es: {} ".format(first_name,last_name,email,username)
        email_from = settings.EMAIL_HOST_USER
        recipent_list=[email]
        send_mail(subject,message,email_from,recipent_list)
        print("el mensaje fue enviado con exito")
        return True
    except:
        print ("el mensaje no fue enviado")
        return False
    



def send_forget_password_mail(email,token):

    subject='Your forget password link'
    message=f'Hola, click en el siguiente link para resetear tu contraseña http://127.0.0.1:8000/lecturas/change_password/{token}/'
    email_from= settings.EMAIL_HOST_USER 
    recipient_list=[email]
    send_mail(subject,message,email_from,recipient_list)
    return True
    
    
#validacion del correo electronico cen formato @utn.edu.ec    
import re
body_regex = re.compile('''
    ^(?!\.)                            # name may not begin with a dot
    (
      [a-z0-9]     # all legal characters except dot
    )+
    (?<!\.)$                            # name may not end with a dot
''', re.VERBOSE | re.IGNORECASE)
domain_regex = re.compile('''
  utn.edu.ec
''', re.VERBOSE | re.IGNORECASE)

def es_correo_valido(email):
    if not isinstance(email, str) or not email or '@' not in email:
        return False
    body, domain = email.rsplit('@', 1)
    match_body = body_regex.match(body)
    match_domain = domain_regex.match(domain)

    if not match_domain:
        try:
            domain_encoded = domain.encode('idna').decode('ascii')
        except UnicodeError:
            return False
        match_domain = domain_regex.match(domain_encoded)

    return (match_body is not None) and (match_domain is not None)


#validacion de la contraseña
def passwd_check(request,passwd):
    return_val=True
    if len(passwd) < 6:
        print('la longitud de la contraseña debe ser de al menos 6 caracteres ')
        messages.success(request,"La longitud de la contraseña debe ser de al menos 6 caracteres.")
        return_val=False
    if not any(char.isdigit() for char in passwd):
        print('la contraseña debe tener al menos un número')
        messages.success(request,"La contraseña debe tener al menos un número.")
        return_val=False
    if not any(char.isupper() for char in passwd):
        print('la contraseña debe tener al menos una letra mayúscula')
        messages.success(request,"La contraseña debe tener al menos una letra mayúscula.")
        return_val=False
    if not any(char.islower() for char in passwd):
        print('la contraseña debe tener al menos una letra minúscula')
        messages.success(request,"La contraseña debe tener al menos una letra minúscula.")
        return_val=False
    if return_val:
        print('Contraseña valida')
        
    return return_val



