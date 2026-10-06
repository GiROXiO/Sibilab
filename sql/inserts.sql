SET search_path TO sibilab, core;

-- INSERTS INICIALES

-- CATALOGO BASE (Editorial, Categoria y Autor)

INSERT INTO Editorial (idEditorial, nombre) VALUES
('ED-001', 'OReilly Media'),
('ED-002', 'Pearson'),
('ED-003', 'McGraw-Hill');

INSERT INTO Categoria (idCategoria, nombre) VALUES
('CAT-001', 'Bases de Datos'),
('CAT-002', 'Redes de Computadoras'),
('CAT-003', 'Programación');

INSERT INTO Autor (idAutor, nombre) VALUES
('AUT-001', 'C.J. Date'),
('AUT-002', 'Andrew S. Tanenbaum'),
('AUT-003', 'Guido van Rossum');

-- CATALOGO PRINCIPAL (Libro y Ejemplar)

INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
('978-0131977591', 'ED-002', 'Introducción a los Sistemas de Bases de Datos', 2003, 'Conceptos fundamentales y diseño relacional', '/media/libros/date.jpg'),
('978-0132126953', 'ED-002', 'Redes de Computadoras', 2011, 'Arquitectura, protocolos y modelo OSI', '/media/libros/redes.jpg');

INSERT INTO Pertenece (ISBN, idCategoria) VALUES
('978-0131977591', 'CAT-001'),
('978-0132126953', 'CAT-002');

INSERT INTO Escribe (ISBN, idAutor) VALUES
('978-0131977591', 'AUT-001'),
('978-0132126953', 'AUT-002');

-- Dejamos el primer ejemplar disponible y el segundo simulando que ya salió de la biblioteca
INSERT INTO Ejemplar (codigoBarras, ISBN, ubicacion, estado) VALUES
('EJ-001', '978-0131977591', 'Sala A-1', 'disponible'),
('EJ-002', '978-0131977591', 'Sala A-1', 'prestado'),
('EJ-003', '978-0132126953', 'Sala B-2', 'disponible');

-- USUARIOS Y HERENCIA

INSERT INTO Usuario (codigo, identificacion, nombre, correo, contrasenia) VALUES
('ADM-01', '100100100', 'Admin Biblioteca', 'admin@uni.edu.co', 'pbkdf2_sha256$hash1'),
('EST-01', '104050607', 'Estudiante Ejemplo', 'estudiante@uni.edu.co', 'pbkdf2_sha256$hash2'),
('DOC-01', '109080706', 'Docente Ejemplo', 'docente@uni.edu.co', 'pbkdf2_sha256$hash3');

INSERT INTO Admin (codigo) VALUES
('ADM-01');

INSERT INTO Cliente (codigo, rol, carrera, estado) VALUES
('EST-01', 'estudiante', 'Ingeniería de Sistemas', 'activo'),
('DOC-01', 'docente', NULL, 'activo');

-- PRESTAMOS Y DEVOLUCIONES

INSERT INTO SolicitudPrestamo (idSolicitud, codigo_c, codigo_a, estado) VALUES
('SOL-001', 'EST-01', 'ADM-01', 'aprobado');
 
INSERT INTO Prestamo (idPrestamo, idSolicitud, codigoBarras, fechaPrestamo, fechaVencimiento) VALUES
('PRE-001', 'SOL-001', 'EJ-002', '2026-10-01', '2026-10-08');

-- INSERT INTO devolucion (idDevolucion, idPrestamo, codigo, fechaDevolucion, observaciones, multa) VALUES
-- ('DEV-001', 'PRE-001', 'ADM-01', '2026-10-04', DEFAULT, 0);


-- INSERTS NUEVOS