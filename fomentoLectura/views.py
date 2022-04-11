from logging import exception
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from fomentoLectura.helpers import send_register_new_user,send_forget_password_mail, es_correo_valido,passwd_check
from fomentoLectura.models import Lectura,Profile,Comentario
from fomentoLectura import analisis_lectura
#import
import speech_recognition as sr
import pyaudio
import wave
import time
import random
import uuid 
from cmath import cos
from jieba import analyse
# Create your views here.

#Login para el ingreso
def loginView(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        if not username or not password:
            messages.success(request,"Se requiere tanto el nombre de usuario como la contraseña")
            return render(request, 'registration/login.html')
        user_obj=User.objects.filter(username=username).first()
        if user_obj is None:
            messages.success(request,"El usuario no esta registrado")
            return render(request, 'registration/login.html')
        user =authenticate(username=username, password=password)
        if user is None:
            messages.success(request,"Contraseña incorrecta")
            return render(request, 'registration/login.html')
        lecturas= Lectura.objects.all()
        login(request , user)
        return render(request,"estudiante/home.html",{"lecturas":lecturas}) 
    return render(request , 'registration/login.html')

#redirecciona a la vista de registro
def view_registro(request):
    return render(request,"registration/registro.html") 

#redirecciona a la vista de Recuperar la contraseña
def view_recuperar_password(request):
    return render(request,"registration/recuperar_password.html") 


#Registro de estudiantes nuevos
def registarUsuario(request):
    numeroaleatorio = random.randint(10, 9999)
    if request.method == 'POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        username=first_name.lower() + last_name.lower() + str(numeroaleatorio)
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        
        if(password==password2):
            
            if not username or not password or not first_name or not last_name or not email:
                messages.success(request,"Se requiere que ingrese todos los datos")
                return redirect('view_registro')
            
            if passwd_check(request,password):
            
                if es_correo_valido(email):
                    user_obj=User.objects.filter(email=email).first()
                    
                    if user_obj:
                        messages.success(request,"El correo que ingreso ya existe, intente con otro correo")
                        return redirect('view_registro')
                    else:  
                        usuario=User.objects.filter(username=username).first()
                        if usuario:
                            username=first_name.lower() + last_name.lower() + str(numeroaleatorio)
                        else:           
                            try:
                                send_register_new_user(first_name,last_name,email,username)
                                if send_register_new_user:
                                
                                    idUser=User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,password=password)
                                    profile_obj = Profile.objects.create(user = idUser)
                                    profile_obj.save()  
                                    messages.success(request,"Su cuenta y usuario fueron creados correctamente, revice su correo")      
                                    return redirect("login")
                                else:
                                    messages.success(request,"Error al momento de crear su cuenta")
                                return redirect("view_registro")    
                            except:
                                messages.success(request,"Error al momento de crear su cuenta")
                                return redirect("view_registro")
                else:
                        
                    messages.success(request,"El correo no es valido ")
                        
        else:
            messages.success(request,"las contraseñas no coinciden ")
            return redirect('view_registro')
    return redirect('view_registro')


#envio del usuaripo para recuperar la contrasña
def forget_password(request):
    try:
        if request.method=='POST':
            username=request.POST.get('username')
            print (username)
            if not username:
                messages.success(request,"Se requiere que ingrese su usuario")
                return redirect('view_olvido_password')
            if not User.objects.filter(username=username).first():
                messages.success(request,'El usuario que ingreso no existe')
                return redirect('view_olvido_password')
            user_obj= User.objects.get(username=username)
            token=str(uuid.uuid4())
            user_email= user_obj.email
            #guardar datos en la nueva tabla
            profile_obj=Profile.objects.get(user=user_obj)
            profile_obj.forget_password_token=token
            profile_obj.save()
            send_forget_password_mail(user_email,token)
            messages.success(request,'Correo enviado con éxito, revice su correo')
            
            return redirect("view_olvido_password")        
    except Exception as e:
        messages.success(request,e)
        print(e)

#cambiar la contraseña 
def change_password_view_user(request,token):
    context={}
    try:
        profile_obj=Profile.objects.filter(forget_password_token=token).first()
        context={'user_id': profile_obj.user.id}
        print(profile_obj)
        if request.method=='POST':
            new_password=request.POST.get('new_password')
            new_password_confirm=request.POST.get('reconfirm_password')
            user_id=request.POST.get('user_id')
            
            if passwd_check(request, new_password): 
                
                if user_id is None:
                    messages.success(request,"No se encontró ninguna identificación de usuario.")
                    return redirect(f'/change_password/{token}/')
                
                if new_password !=new_password_confirm:
                    messages.success(request,"Las contraseñas que ingreso no coinciden")
                    return redirect(f'/change_password/{token}/')
                
                user_obj=User.objects.get(id=user_id)
                user_obj.set_password(new_password)
                user_obj.save()    
                return render(request,"registration/change_password_complete.html")
    
    except Exception as e:
        print(e)
    return render(request,"registration/change_password_user.html",context)


#view home
@login_required(login_url='login')
def home(request):
    
    lista_lecturas= Lectura.objects.all()
    paginator=Paginator(lista_lecturas,10)
    pagina=request.GET.get("page") or 1
    lecturas=paginator.get_page(pagina)
    pagina_actual=int(pagina)
    paginas=range(1,lecturas.paginator.num_pages+1) 
    return render(request,"estudiante/home.html",{"lecturas":lecturas,"paginas":paginas,"pagina_actual":pagina_actual}) 

def Logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def view_introdution(request):
    return render(request,"estudiante/introduccion.html")

@login_required(login_url='login')
def view_pdf(request, lectura_id):
    comentarios= Comentario.objects.filter(lectura=lectura_id)
    lectura=Lectura.objects.get(id=lectura_id)
    return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios}) 

@login_required(login_url='login')
def view_change_password_home(request):
    return render(request,"estudiante/cambiar_contrasenia_est.html")

@login_required(login_url='login')
def edit_user_home(request):
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        
        if not username or not first_name or not last_name or not email:
            messages.success(request,"No se permiten datos vacios")
            return redirect('change_Password_user')
        user_obj=User.objects.get(username=username)
        #user_obj.set
        return redirect('home')
    return redirect('change_Password_user')

@login_required(login_url='login')      
def change_password_user_home(request):
    if request.method=='POST':
        user_id=request.POST.get('user_id')
        password_new=request.POST.get('password_new')
        password_new2=request.POST.get('password_new2')
        if passwd_check(request, password_new): 
            if not password_new or not password_new2:
                messages.success(request,"No se permiten datos vacios")
                return redirect('change_Password_user')
            user_obj=User.objects.get(id=user_id)        
            user_obj.set_password(password_new)
            user_obj.save()
            messages.success(request,"Contraseña cambiada con exito.")
            return redirect('change_Password_user')
        return redirect('change_Password_user')
    return redirect('change_Password_user')


@login_required(login_url='login')
def buscar_lectura(request):
    if request.method=='POST':
        busqueda=request.POST.get('buscar')
        lecturas=Lectura.objects.all()
        if busqueda:
            lecturas= Lectura.objects.filter(
                Q(titulo__icontains=busqueda)).distinct()
        
        return render(request,"estudiante/home.html",{"lecturas":lecturas}) 

@login_required(login_url='login')
def comentar(request):
    if request.method=='POST':
        comentario=request.POST.get('comentario')
        id_lectura=request.POST.get('id_lectura')
        id_usuario=request.POST.get('user')
        
        if not comentario:
            messages.success(request,"Ingrese un comentario antes de guardar.")  
        else:
            comentario= Comentario.objects.create(comentario=comentario,lectura_id=id_lectura,user_id=id_usuario)
            comentario_ingresado=comentario.id
            print (comentario_ingresado)
        comentarios= Comentario.objects.filter(lectura=id_lectura)
        lectura=Lectura.objects.get(id=id_lectura)
        return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios})     
    return redirect("home") 
    
@login_required(login_url='login')
def view_actualizar_comentario(request,id):
    id_com=Comentario.objects.get(id=id)
    return render(request,"estudiante/model_confirm.html",{"comentario":id_com})  

@login_required(login_url='login')
def actualizar_comentario(request):
    if request.method=='POST':
        id_comentario=request.POST.get('id_comentario')
        id_lectura=request.POST.get('id_lectura')
        update_comentario=request.POST.get('comentario')

        id_user=request.POST.get('id_user')
        id_comentario_user=request.POST.get('id_comentario_user')
        
        fecha_actualizada= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        if id_user==id_comentario_user:    
            comentario=Comentario.objects.get(id=id_comentario)
            comentario.comentario=update_comentario
            comentario.updated=fecha_actualizada
            comentario.save()
            messages.success(request,"Su comentario fue actualizado con éxito.") 
        else:
            messages.success(request,"Querido usuari@ usted no puede actualizar un comentario que no le pertenece.") 
        lectura=Lectura.objects.get(id=id_lectura)
        comentarios= Comentario.objects.filter(lectura=id_lectura)
        return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios})  
        
        
@login_required(login_url='login')
def eliminar_comentario(request):
    if request.method=='POST':
        #user que esta logueado
        user_logueo=request.POST.get('user_logueado')
        #user que comento
        user_comentario=request.POST.get('user_comentario')
        #datos para volver a cargar la pagina
        id_comentario=request.POST.get('id_comentario')
        id_lectura=request.POST.get('id_lectura')        
        lectura=Lectura.objects.get(id=id_lectura)
        comentarios= Comentario.objects.filter(lectura=id_lectura)
        if not user_logueo or not user_comentario or not id_comentario or not id_lectura:
            messages.success(request,"Error.")
            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios})  
        #obtengo el id del comentario de la base 
        if user_logueo==user_comentario:
            comentario=Comentario.objects.get(id=id_comentario)  
            print("Este es el comentario: " +comentario)  
            if not id_comentario or not comentario.id:
                messages.success(request,"El comentario ya no existe.")
                return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios}) 
            else:
                comentario.delete()
                messages.success(request,"Su comentario a sido eliminado con éxito.")  
                return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios}) 
        else: 
            messages.success(request,"Querido usuari@ usted no puede eliminar un comentario que no le pertenece.")       

        return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios})  
    return redirect('home')


@login_required(login_url='login')
def eliminar_com(request,id,id_user):
    try:
        obj_comentario=Comentario.objects.get(id=id)
        user_obj=User.objects.get(id=id_user)
        
        id_lectura=obj_comentario.lectura.id
        
        id_comentario=obj_comentario.user.id
        user_logueado=user_obj.id
        
        lectura=Lectura.objects.get(id=id_lectura)
        comentarios= Comentario.objects.filter(lectura=id_lectura)
        
        
        if id_comentario==user_logueado:
            obj_comentario.delete()
            messages.success(request,"Su comentario a sido eliminado con éxito.")   
            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios}) 
        else:
            messages.success(request,"Querido usuario, usted no tiene permitido eliminar un comentario que no le pertenece.")   
    
    except:
        messages.success(request,"El comentario que quiere eliminado ya fue eliminado con éxito.")
        return redirect("home")
    
    return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios})     


#para contar las palabras y guardar el audio
@login_required(login_url='login')
def cantidad_palabras_x_minuto(request):
    #DEFINIMOS PARAMETROS
    if request.method=='POST':
        usuario= request.POST.get("usuario")
        id_lectura=request.POST.get('id_lectura')
        lapso_tiempo_audio=60 #segundos
        
        #volver a cargar la pagina 
        lectura=Lectura.objects.get(id=id_lectura)
        comentarios= Comentario.objects.filter(lectura=id_lectura)
        
        recognizer = sr.Recognizer()

        ''' grabando el sonido'''
        with sr.Microphone(device_index=2) as source:
            try:
                print("Adjusting noise ")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Grabacion durante 60 segundos")
                recorded_audio = recognizer.listen(source,timeout=5, phrase_time_limit=60)
                print("Done recording")
                
            except Exception as ex:
                textodicho= "No entiendo" 
                
        ''' Reconocimiento el audio '''
        try:
            print("Reconociendo el texto")
            text = recognizer.recognize_google(
                    recorded_audio, 
                    language="es-ec"
                )
            #  
            textodicho=format(text)
            #conteo de palabras 
            result = len(textodicho.split())
            cantidad_palabras=str(result)+" por minuto. "
            print(textodicho)
            print(cantidad_palabras)
            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"cantidad_palabras":cantidad_palabras,"texto":textodicho}) 
        except Exception as ex:
            print(ex)
            cantidad_palabras="Perdón! No entiendo lo que dices "
            print("I am sorry! I can not understand!")
            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"cantidad_palabras":cantidad_palabras}) 
    else: 
        return redirect("home")




@login_required(login_url='login')
def analisis_texto(request):
    if request.method=='POST':
        text_base=request.POST.get('text_base')
        text_analysis=request.POST.get('text_analisis')
        id_lectura=request.POST.get('id_lectura')
        cantidad_palabras_x_minuto=request.POST.get('numero_palabras')
                
        #volver a cargar la pagina 
        lectura=Lectura.objects.get(id=id_lectura)
        comentarios= Comentario.objects.filter(lectura=id_lectura)
                
        if text_base:
            if text_analysis:        

                # Introducir la interfaz de extracción de palabras clave TF-IDF
                tfidf = analyse.extract_tags
                # Utilice un conjunto personalizado de palabras de parada
                analyse.set_stop_words("fomentoLectura\stop_words.txt")
                # Texto original
                text_original = text_base
                # Extracción de palabras clave basada en el algoritmo TF-IDF
                keywords = tfidf(text_original)
                print ("keywords by tfidf:")
                # Salida de las palabras clave extraídas
                for keyword in keywords:
                    print (keyword + "/")
                
                ##----------------------------------------------------
                #palabras principales
                cont=0
                count_word_reading=0
                sumcosine=0
                for keyword in keywords:
                    print (keyword + "/"),
                    cont+=1   
                    text1 = keyword
                    text2 = text_analysis
                    vector1 = analisis_lectura.text_to_vector(text1)
                    vector2 = analisis_lectura.text_to_vector(text2)
                    cosine= analisis_lectura.get_cosine(vector1, vector2)
                    
                    if cosine >0:
                        count_word_reading+=1
                    print (cosine)
                    sumcosine+=cosine
                    
                porcent=float(sumcosine)/cont
                print("---el porcentaje es:--")
                print(porcent)
                print ("cantidad de palabras claves: "+str(count_word_reading))
                vect3=analisis_lectura.text_to_vector(text_original)
                vect4=analisis_lectura.text_to_vector(text2)
                cosine_textorg= analisis_lectura.get_cosine(vect3, vect4)

                print ('Concuerda un: ', cosine_textorg)

                message=""

                if cosine_textorg<0.6:
                    if porcent>0.015 and count_word_reading>3 :
                        message="El texto ingresado concuerda con lo que leyó"
                        print("El texto ingresado concuerda con lo que leyo")
                                
                        if porcent>0 and porcent<0.015:
                            message="Expliquese mejor"
                            print("Expliquese mejor")
                            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto})
                        return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto})
                    else:
                        
                        if porcent>0 and porcent<0.015:
                            message="Expliquese mejor"
                            print("Expliquese mejor")
                            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto})
                        if porcent==0.0:
                            message="El texto ingresado no esta acorde al leído"
                            print("Lo que ingreso no concuerda con lo que leyó o expliquese mejor")
                            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto})
                        else:
                            print("error")
                            message="Ingrese algo acorde al texto que leyó"
                            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto})
                else:
                    message="El texto ingresado es copia del original"
                    print("El texto ingresado es copia del original")
                    return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto})
            else:
                message="Ingrese un texto para analizar"
                return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto}) 
        else:
            message="Realice primero una lectura rápida"
            return render(request,"estudiante/view_pdf.html",{"lectura":lectura,"comentarios":comentarios,"texto":text_base,"texto2":text_analysis,"mensaje":message,"cantidad_palabras":cantidad_palabras_x_minuto})
    
    else:
        return redirect("home")

def view_intrucciones(request):
    return render (request,"estudiante/intrucciones.html")