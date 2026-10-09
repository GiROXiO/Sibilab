# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    codigo = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='codigo', primary_key=True)

    class Meta:
        managed = False
        db_table = 'admin'


class Autor(models.Model):
    idautor = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'autor'


class Categoria(models.Model):
    idcategoria = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'categoria'


class Cliente(models.Model):
    codigo = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='codigo', primary_key=True)
    rol = models.CharField(max_length=10)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=9)

    class Meta:
        managed = False
        db_table = 'cliente'


class Devolucion(models.Model):
    iddevolucion = models.CharField(primary_key=True, max_length=10)
    idprestamo = models.OneToOneField('Prestamo', models.DO_NOTHING, db_column='idprestamo')
    codigo = models.ForeignKey(Admin, models.DO_NOTHING, db_column='codigo')
    fechadevolucion = models.DateField()
    observaciones = models.CharField(max_length=200)
    multa = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'devolucion'


class Editorial(models.Model):
    ideditorial = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'editorial'


class Ejemplar(models.Model):
    codigobarras = models.CharField(primary_key=True, max_length=20)
    isbn = models.ForeignKey('Libro', models.DO_NOTHING, db_column='isbn')
    ubicacion = models.CharField(max_length=10)
    estado = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'ejemplar'


class Escribe(models.Model):
    pk = models.CompositePrimaryKey('isbn', 'idautor')
    isbn = models.ForeignKey('Libro', models.DO_NOTHING, db_column='isbn')
    idautor = models.ForeignKey(Autor, models.DO_NOTHING, db_column='idautor')

    class Meta:
        managed = False
        db_table = 'escribe'


class Libro(models.Model):
    isbn = models.CharField(primary_key=True, max_length=20)
    ideditorial = models.ForeignKey(Editorial, models.DO_NOTHING, db_column='ideditorial')
    titulo = models.CharField(max_length=100)
    anio = models.IntegerField()
    descripcion = models.CharField(max_length=1000, blank=True, null=True)
    url_imagen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'libro'


class Pertenece(models.Model):
    pk = models.CompositePrimaryKey('isbn', 'idcategoria')
    isbn = models.ForeignKey(Libro, models.DO_NOTHING, db_column='isbn')
    idcategoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='idcategoria')

    class Meta:
        managed = False
        db_table = 'pertenece'


class Prestamo(models.Model):
    idprestamo = models.CharField(primary_key=True, max_length=10)
    idsolicitud = models.OneToOneField('Solicitudprestamo', models.DO_NOTHING, db_column='idsolicitud')
    codigobarras = models.ForeignKey(Ejemplar, models.DO_NOTHING, db_column='codigobarras')
    fechaprestamo = models.DateField()
    fechavencimiento = models.DateField()

    class Meta:
        managed = False
        db_table = 'prestamo'


class Solicitudprestamo(models.Model):
    idsolicitud = models.CharField(primary_key=True, max_length=10)
    codigo_c = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='codigo_c')
    codigo_a = models.ForeignKey(Admin, models.DO_NOTHING, db_column='codigo_a', blank=True, null=True)
    isbn = models.ForeignKey(Libro, models.DO_NOTHING, db_column='isbn')
    estado = models.CharField(max_length=9)

    class Meta:
        managed = False
        db_table = 'solicitudprestamo'


class Usuario(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    identificacion = models.CharField(unique=True, max_length=10)
    nombre = models.CharField(max_length=60)
    correo = models.CharField(unique=True, max_length=100)
    contrasenia = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'usuario'
