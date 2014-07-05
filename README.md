Software de gestió per cooperatives de consum responsable

Install
-------

Cal instal·lar (en un virtualenv):

- django 1.6 minim
- django_multiform

Ajustos:
- copiar django1/email_settings.sample.py a django1/email_settings.py
- afegir site amb el menu de admin
- ajustar SITE_ID adequadament

Run
---

$ python manage.py runserver


Deploy
------
- clone project
- adjust permissions: folder , db.sqlite3
- configure virtualhost apache
- conf. apache virtualenv
- configure static files
- configure email_settings.py
- configure site in admin backend and adjust SITE_ID in settings.py
