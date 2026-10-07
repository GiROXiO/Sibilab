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

--INSERT INTO SolicitudPrestamo (idSolicitud, codigo_c, codigo_a, estado) VALUES
--('SOL-001', 'EST-01', 'ADM-01', 'aprobado');
 
--INSERT INTO Prestamo (idPrestamo, idSolicitud, codigoBarras, fechaPrestamo, fechaVencimiento) VALUES
--('PRE-001', 'SOL-001', 'EJ-002', '2026-10-01', '2026-10-08');

-- INSERT INTO devolucion (idDevolucion, idPrestamo, codigo, fechaDevolucion, observaciones, multa) VALUES
-- ('DEV-001', 'PRE-001', 'ADM-01', '2026-10-04', DEFAULT, 0);


-- INSERTS NUEVOS

INSERT INTO Editorial (idEditorial, nombre) VALUES
('ED001', 'OReilly'),
('ED002', 'McGraw Hill'),
('ED003', 'Pearson');

INSERT INTO Categoria (idCategoria, nombre) VALUES
('CAT001', 'Programacion'),
('CAT002', 'Bases de Datos'),
('CAT003', 'Redes');

INSERT INTO Autor (idAutor, nombre) VALUES
('AUT001', 'Robert C Martin'),
('AUT002', 'Andrew S Tanenbaum'),
('AUT003', 'Abraham Silberschatz'),
('AUT004', 'Martin Kleppmann');

INSERT INTO Libro
(ISBN, idEditorial, titulo, anio, descripcion, url_imagen)
VALUES
('978001', 'ED001', 'Clean Code', 2008, 'Buenas practicas de programacion', NULL),
('978002', 'ED002', 'Sistemas Operativos', 2018, 'Conceptos de sistemas operativos', NULL),
('978003', 'ED002', 'Fundamentos de Bases de Datos', 2020, 'Fundamentos de bases de datos', NULL),
('978004', 'ED003', 'Redes de Computadores', 2019, 'Conceptos de redes de computadores', NULL),
('978005', 'ED001', 'Diseno de Sistemas', 2021, 'Diseno y arquitectura de software', NULL);

INSERT INTO Pertenece (ISBN, idCategoria) VALUES
('978001', 'CAT001'),
('978002', 'CAT001'),
('978003', 'CAT002'),
('978004', 'CAT003'),
('978005', 'CAT001');

INSERT INTO Escribe (ISBN, idAutor) VALUES
('978001', 'AUT001'),
('978002', 'AUT002'),
('978003', 'AUT003'),
('978004', 'AUT002'),
('978005', 'AUT004');

INSERT INTO Ejemplar
(codigoBarras, ISBN, ubicacion, estado)
VALUES
('BAR001', '978001', 'A1', 'disponible'),
('BAR002', '978001', 'A1', 'prestado'),
('BAR003', '978002', 'A2', 'prestado'),
('BAR004', '978003', 'B1', 'disponible'),
('BAR005', '978004', 'B2', 'prestado'),
('BAR006', '978005', 'B2', 'disponible'),
('BAR007', '978001', 'A1', 'disponible'),
('BAR008', '978003', 'B1', 'disponible');

INSERT INTO Usuario
(codigo, identificacion, nombre, correo, contrasenia)
VALUES
('U001', '1001', 'Juan Perez', 'juan@gmail.com', '1234'),
('U002', '1002', 'Maria Lopez', 'maria@gmail.com', '1234'),
('U003', '1003', 'Carlos Gomez', 'carlos@gmail.com', '1234'),
('U004', '1004', 'Ana Torres', 'ana@gmail.com', '1234');

INSERT INTO Cliente
(codigo, rol, carrera, estado)
VALUES
('U001', 'estudiante', 'Ingenieria de Sistemas', 'activo'),
('U002', 'estudiante', 'Ingenieria de Sistemas', 'activo'),
('U003', 'docente', 'Ingenieria de Sistemas', 'activo');

INSERT INTO Admin (codigo) VALUES
('U004');

INSERT INTO SolicitudPrestamo
(idSolicitud, codigo_c, codigo_a, ISBN, fechaSolicitud, estado)
VALUES
('SOL001', 'U001', 'U004', '978001', '2026-10-01', 'aprobado'),
('SOL002', 'U002', 'U004', '978002', '2026-10-02', 'aprobado'),
('SOL003', 'U001', 'U004', '978003', '2026-10-03', 'aprobado'),
('SOL004', 'U002', 'U004', '978001', '2026-10-05', 'aprobado'),
('SOL005', 'U003', 'U004', '978004', '2026-10-06', 'aprobado');

INSERT INTO Prestamo
(idPrestamo, idSolicitud, codigoBarras, fechaPrestamo)
VALUES
('PRE001', 'SOL001', 'BAR002', '2026-10-01'),
('PRE002', 'SOL002', 'BAR003', '2026-10-02'),
('PRE003', 'SOL003', 'BAR004', '2026-10-03'),
('PRE004', 'SOL004', 'BAR001', '2026-10-05'),
('PRE005', 'SOL005', 'BAR005', '2026-10-06');

INSERT INTO devolucion
(idDevolucion, idPrestamo, codigo, fechaDevolucion, observaciones, multa)
VALUES
('DEV001', 'PRE001', 'U004', '2026-10-07', 'Devuelto a tiempo', 0),
('DEV002', 'PRE002', 'U004', '2026-10-12', 'Entrega tardia', 5000),
('DEV003', 'PRE003', 'U004', '2026-10-10', 'Devuelto a tiempo', 0);