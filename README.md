# **Manual de instalación de Time2Sport**

Este proyecto está diseñado para ejecutarse en Ubuntu 22.04. A continuación, se detallan los pasos necesarios para su instalación y configuración.

## **1. Instalación de Git**
Si no tienes `git` instalado, puedes hacerlo con el siguiente comando:

```
sudo apt update
sudo apt install git
```

Luego, clona el repositorio con:

```
git clone https://github.com/esthermtnz/Time2Sport.git
cd Time2Sport
```

## **2. Comprobación e instalación de Python**
Se requiere Python 3.8 o superior. Para verificar la versión instalada, usa:

```
python3 --version
```

Si no tienes Python 3.8 o una versión más reciente, instálalo con:

```
sudo apt update
sudo apt install python3
sudo apt install python3-pip
```

## **3. Creación de un entorno virtual**
Antes de crear el entorno virtual, asegúrate de tener python3.10-venv instalado. Si no lo tienes, puedes instalarlo con:

```
sudo apt install python3.10-venv
```

Una vez que tengas Python, crea un entorno virtual:

```
python3 -m venv venv
```

Para activarlo:

```
source venv/bin/activate
```

Si necesitas salir del entorno virtual, usa:

```
deactivate
```

## **4. Instalación de dependencias**
Dirígete al directorio `time2sport`, instala `pip` dentro del entorno virtual y las dependencias:
```
cd time2sport
pip install --upgrade pip
pip install -r requirements.txt
```

## **5. Instalación y configuración de Redis**
Para descargar e iniciar Redis, usa:

```
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

Verifica que está en funcionamiento con:

```
redis-cli ping
```

Debe devolver `PONG`.

También puedes comprobar que salga activo con el siguiente comando:
```
sudo systemctl status redis-server
```

## **6. Migraciones y carga de datos iniciales**
Ejecuta las migraciones necesarias:

```
python3 manage.py makemigrations sgu sbai src slegpn
python3 manage.py migrate
```

> Nota: Es posible ejecutar simplemente `python3 manage.py makemigrations`, pero al especificar las aplicaciones (`sgu sbai src slegpn`) estamos forzando la ejecución de las migraciones para esas apps en particular. De esta manera se evitan posibles errores y se garantiza que todas las migraciones necesarias se realicen correctamente.

Ejecuta el populate para cargar los datos iniciales en la base de datos. Usa el siguiente comando:

```
python3 populate.py

```

Existe un script `db.sh` que automatiza este apartado; contiene el borrado de migraciones y de la base de datos, la creación de migraciones y la población de la base de datos. Para ejecutarlo:

```
./db.sh
```

## **7. Ejecución del servidor y workers de Celery**
Inicia el servidor con:

```
python3 manage.py runserver
```

En otra terminal, ejecuta los workers de Celery:

```
celery -A time2sport worker --loglevel=info
```

Recuerda que en esta segunda terminal deberás volver a activar el entorno virtual mediante el comando: 

```
source ../venv/bin/activate
```

> Nota: Antes de ejecutar source, asegúrate de que estás ubicado dentro de `Time2Sport/time2sport`, para que la activación del entorno virtual funcione correctamente.

Si lo prefieres, puedes ejecutar ambos comandos en la misma terminal de la siguiente manera:

```
celery -A time2sport worker --loglevel=info &
python3 manage.py runserver
```

> Nota: El símbolo & al final del comando de Celery hace que Celery se ejecute en segundo plano, mientras que el servidor (runserver) se ejecutará en primer plano. 

## **8. Acceso a la aplicación**

Una vez que el servidor esté en ejecución, puedes acceder a la aplicación desde tu navegador utilizando la siguiente URL:

```
http://localhost:8000
```

## **9. Creación de un superusuario**

Si quieres acceder a las pestañas de administración, puedes crear un superusuario ejecutando el siguiente comando:

```
python3 manage.py createsuperuser
```

Luego, completa los campos solicitados como nombre de usuario, correo electrónico y contraseña.

Una vez creado, puedes acceder al panel de administración desde tu navegador:

```
http://localhost:8000/admin
```

## **10. Ejecución de tests**

Para ejecutar los tests de una aplicación específica, usa:

```
python3 manage.py test <app>
```

Si quieres ejecutar los tests por incrementos, sigue esta estructura:

- Primer incremento:
  ```
  python3 manage.py test sgu sbai
  ```
- Segundo incremento:
  ```
  python3 manage.py test src slegpn
  ```

Si se quisiera ejecutar todos los tests a la vez, usa:
```
python3 manage.py test
```

## **11. Opcional: Prueba de pago en entorno de pruebas**

Si deseas probar el proceso de pago puedes utilizar las siguientes credenciales:

**Cuenta de pago (Payer Account)**
- Email: `sb-o4c6a38227363@personal.example.com`
- Contraseña: `m4t1(!Yo`

El dinero simulado irá a la siguiente cuenta:

**Cuenta receptora (Receiver Account)**
- Email: `sb-ruupa38090694@business.example.com`
- Contraseña: `ym7hX@]/`

> Nota: Ten en cuenta que este es un entorno de pruebas, por lo que el pago no es real y no afecta cuentas bancarias reales.

## **12. Opcional: Instalación de VS Code para ver el código**

Si quieres visualizar y editar el código de manera cómoda, puedes instalar Visual Studio Code (VS Code) con los siguientes comandos:

En primer lugar asegurate de tener instalado Snap:

```
snap --version
```

En caso de no tenerlo, instalarlo con:

```
sudo apt install snapd
```

```
sudo snap install code --classic
```

También puedes descargarlo desde su [página web oficial](https://code.visualstudio.com/Download).

Una vez instalado, puedes abrir el proyecto desde el icono de la aplicación o con el siguiente comando en la terminal:
```
code .
```
