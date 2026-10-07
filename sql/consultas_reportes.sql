SET search_path TO core, sibilab;
commit;

--Consultas

--Todos los libros
select * from libro;

--Todos los usuarios
select * from usuario;

--Todos los clientes
select * from cliente;

--Todas las categorías de libros
select * from categoria;

--Todos los prestamos que tienen devolución
select * from prestamo p inner join devolucion d on p.idprestamo = d.idprestamo;

--Todos los usuarios que son administradores
select * from usuario u join admin a on u.codigo = a.codigo;

--Todos los estudiantes de Ingeniería de Sistemas
select * from cliente where carrera = 'Ingeniería de Sistemas' and rol = 'estudiante';

--Cantidad de libros por editorial
select ideditorial, count(*) as cantidad_libros from libro group by ideditorial;

--Cantidad de ejemplares por estado
select estado, count(*) as cantidad from ejemplar group by estado;

--Cantidad de clientes por rol
select rol, count(*) as cantidad from cliente group by rol;

--Cantidad de prestamos por ejemplar
select codigobarras, count(*) as cantidad_prestamos from prestamo group by codigobarras;

--Libros más prestados
select l.titulo, count(*) as cantidad_prestamos from libro l 
join ejemplar e on l.isbn = e.isbn
join prestamo p on e.codigobarras = p.codigobarras
group by l.isbn, l.titulo order by cantidad_prestamos desc;

--Estudiantes que tienen deudas
select u.nombre, sum(d.multa) as deuda_total from usuario u
join cliente c on u.codigo = c.codigo
join solicitudprestamo s on c.codigo = s.codigo_c
join prestamo p on s.idsolicitud = p.idsolicitud
join devolucion d on p.idprestamo = d.idprestamo
where c.rol = 'estudiante' and d.multa > 0 group by u.codigo, u.nombre order by deuda_total desc;

--Historial mensual de prestamos
select
    extract(year from fechaprestamo) as anio,
    extract(month from fechaprestamo) as mes,
    count(*) as cantidad_prestamos
from prestamo
group by
    extract(year from fechaprestamo),
    extract(month from fechaprestamo)
order by anio, mes;