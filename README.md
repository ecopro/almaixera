Software de gestió per cooperatives de consum responsable

Install
-------

Cal instal·lar (en un virtualenv):

- django 1.6 minim
- django_multiform

Ajustos:
- copiar django1/email_settings.sample.py a django1/email_settings.py
- modificar Site (a django admin) i posar el nou domini

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
- configure Site in admin backend to the new domain

Database Migrations
-------------------
Per migrar els canvis de la base de dades hi ha instal·lat South:
$ python manage.py schemamigration comandes --auto
$ python manage.py migrate comandes
