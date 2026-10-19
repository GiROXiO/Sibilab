SET search_path TO sibilab, core;

--Consultas basicas

--Todos los admin
select * from admin;

--Todos los autores
select * from autor;

--Todas las categorias
select * from categoria;

--Todos los clientes
select * from cliente;

--Todas las devoluciones
select * from devolucion;

--Todas las editoriales
select * from editorial;

--Todos los ejemplares
select * from ejemplar;

--Tabla escribe (Autor y sus libros)
select * from escribe;

--Todos los libros
select * from libro;

--Tabla pertenece (Categoria y sus libros)
select * from pertenece;

--Todos los prestamos
select * from prestamo;

--Todas las solicitudes de prestamo
select * from solicitudprestamo;

--Todos los usuarios
select * from usuario;


--Todos los prestamos que tienen devolución
select * from prestamo p inner join devolucion d on p.idprestamo = d.idprestamo;

--Todos los estudiantes de Ingeniería de Sistemas
select * from cliente where carrera = 'Ingeniería de Sistemas' and rol = 'estudiante';

--Consultas para análisis de datos:

--Libros más prestados
--Eje X: titulo
--Eje Y: cantidad_prestamos

select l.titulo, count(*) as cantidad_prestamos from libro l 
join ejemplar e on l.isbn = e.isbn
join prestamo p on e.codigobarras = p.codigobarras
group by l.isbn, l.titulo order by cantidad_prestamos desc;

--Multas acumuladas por estudiante
--Eje X: nombre
--Eje Y: deuda_total

select u.nombre, sum(d.multa) as deuda_total from usuario u
join cliente c on u.codigo = c.codigo
join solicitudprestamo s on c.codigo = s.codigo_c
join prestamo p on s.idsolicitud = p.idsolicitud
join devolucion d on p.idprestamo = d.idprestamo
where c.rol = 'estudiante' and d.multa > 0 group by u.codigo, u.nombre order by deuda_total desc;

--Historial mensual de prestamos
--Eje X: mes
--Eje Y: cantidad_prestamos

select
    date_trunc('month', fechaprestamo)::date as intervalo,
    count(*) as cantidad_prestamos
from prestamo
group by date_trunc('month', fechaprestamo)
order by intervalo;

--Ejemplares por estado
--Eje X: estado
--Eje Y: cantidad_ejemplares

select estado, count(*) as cantidad_ejemplares
from ejemplar
group by estado
order by cantidad_ejemplares desc;

--Libros publicados por año
--Eje X: anio
--Eje Y: cantidad_libros

select anio, count(*) as cantidad_libros
from libro
group by anio
order by anio;

--Libros por editorial
--Eje X: editorial
--Eje Y: cantidad_libros

select ed.nombre as editorial,
       count(l.isbn) as cantidad_libros
from editorial ed
join libro l on ed.ideditorial = l.ideditorial
group by ed.ideditorial, ed.nombre
order by cantidad_libros desc;

-- Solicitudes por estado
-- Eje X: estado
-- Eje Y: cantidad_solicitudes

select estado, count(*) as cantidad_solicitudes
from solicitudprestamo
group by estado
order by cantidad_solicitudes desc;

-- Prestamos por editorial
-- Eje X: editorial
-- Eje Y: cantidad_prestamos

select ed.nombre as editorial, count(*) as cantidad_prestamos
from editorial ed
join libro l on ed.ideditorial = l.ideditorial
join ejemplar e on l.isbn = e.isbn
join prestamo p on e.codigobarras = p.codigobarras
group by ed.ideditorial, ed.nombre
order by cantidad_prestamos desc;

-- Libros más prestados por categoría
-- Eje X: titulo
-- Eje Y: cantidad_prestamos

select
    l.titulo,
    c.nombre as categoria,
    count(p.idprestamo) as cantidad_prestamos
from libro l
join pertenece pe on l.isbn = pe.isbn
join categoria c on pe.idcategoria = c.idcategoria
join ejemplar e on l.isbn = e.isbn
join prestamo p on e.codigobarras = p.codigobarras
group by l.isbn, l.titulo, c.nombre
order by cantidad_prestamos desc;

-- Promedio de días de préstamo por usuario
-- Eje X: nombre
-- Eje Y: promedio_dias

select
    u.nombre,
    round(avg(d.fechadevolucion - p.fechaprestamo), 2) as promedio_dias
from usuario u
join cliente c on u.codigo = c.codigo
join solicitudprestamo s on c.codigo = s.codigo_c
join prestamo p on s.idsolicitud = p.idsolicitud
join devolucion d on p.idprestamo = d.idprestamo
group by u.codigo, u.nombre
order by promedio_dias desc;

-- Promedio de multas por rol
-- Eje X: rol
-- Eje Y: promedio_multa

select
    c.rol,
    count(d.iddevolucion) as devoluciones_registradas,
    round(avg(d.multa), 2) as promedio_multa,
    sum(d.multa) as total_multas
from cliente c
join solicitudprestamo s on c.codigo = s.codigo_c
join prestamo p on s.idsolicitud = p.idsolicitud
join devolucion d on p.idprestamo = d.idprestamo
group by c.rol
order by promedio_multa desc;