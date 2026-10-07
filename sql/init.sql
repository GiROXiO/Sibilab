CREATE SCHEMA core;
SET search_path TO sibilab, core;

-- CATÁLOGO BASE (Entidades Independientes)

CREATE TABLE Editorial (
	idEditorial VARCHAR(10) PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Categoria (
	idCategoria VARCHAR(10) PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Autor (
	idAutor VARCHAR(10) PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL
);

-- CATÁLOGO PRINCIPAL (Libros y Ejemplares)

CREATE TABLE Libro (
	ISBN VARCHAR(20) PRIMARY KEY,
	idEditorial VARCHAR(10) NOT NULL,
	titulo VARCHAR(100) NOT NULL,
	anio int NOT NULL,
	descripcion VARCHAR(200),
	url_imagen VARCHAR(255),
	CONSTRAINT fk_libro_editorial FOREIGN KEY (idEditorial) REFERENCES Editorial(idEditorial)
);

CREATE TABLE Pertenece (
	ISBN VARCHAR(20),
	idCategoria VARCHAR(10),
	PRIMARY KEY(ISBN, idCategoria),
	CONSTRAINT fk_pertenece_libro FOREIGN KEY (ISBN) REFERENCES Libro(ISBN),
	CONSTRAINT fk_pertenece_categoria FOREIGN KEY (idCategoria) REFERENCES Categoria(idCategoria)
);

CREATE TABLE Escribe (
	ISBN VARCHAR(20),
	idAutor VARCHAR(10),
	PRIMARY KEY(ISBN, idAutor),
	CONSTRAINT fk_escribe_libro FOREIGN KEY (ISBN) REFERENCES Libro(ISBN),
	CONSTRAINT fk_escribe_autor FOREIGN KEY (idAutor) REFERENCES Autor(idAutor)
); 

CREATE TABLE Ejemplar (
	codigoBarras VARCHAR(20) PRIMARY KEY,
	ISBN VARCHAR(20) NOT NULL,
	ubicacion VARCHAR(10) NOT NULL,
	estado VARCHAR(10) NOT NULL,
	CONSTRAINT fk_ejemplar_libro FOREIGN KEY (ISBN) REFERENCES Libro(ISBN),
	CONSTRAINT chk_ejemplar_estado CHECK (estado IN ('disponible', 'prestado', 'perdido'))
);

-- USUARIOS Y HERENCIA

CREATE TABLE Usuario (
	codigo VARCHAR(10) PRIMARY KEY,
	identificacion VARCHAR(10) NOT NULL UNIQUE,
	nombre VARCHAR(50) NOT NULL,
	correo VARCHAR(100) NOT NULL UNIQUE,
	contrasenia VARCHAR(100) NOT NULL
);

CREATE TABLE Cliente (
	codigo VARCHAR(10) PRIMARY KEY,
	rol VARCHAR(10) NOT NULL,
	carrera VARCHAR(100),
	estado VARCHAR(9) NOT NULL,
	CONSTRAINT fk_cliente_usuario FOREIGN KEY (codigo) REFERENCES Usuario(codigo),
	CONSTRAINT chk_cliente_rol CHECK (rol IN ('estudiante', 'docente')),
	CONSTRAINT chk_cliente_estado CHECK (estado IN ('activo', 'bloqueado'))
);

CREATE TABLE Admin (
	codigo VARCHAR(10) PRIMARY KEY,
	CONSTRAINT fk_admin_usuario FOREIGN KEY (codigo) REFERENCES Usuario(codigo)
);

-- PRESTAMOS Y DEVOLUCIONES

CREATE TABLE SolicitudPrestamo (
	idSolicitud VARCHAR(10) PRIMARY KEY,
	codigo_c VARCHAR(10) NOT NULL,
	codigo_a VARCHAR(10),
	ISBN VARCHAR(20) NOT NULL,
	fechaSolicitud DATE NOT NULL,
	estado VARCHAR(9) NOT NULL DEFAULT 'pendiente',
	CONSTRAINT fk_solicitud_cliente FOREIGN KEY (codigo_c) REFERENCES Cliente(codigo),
	CONSTRAINT fk_solicitud_admin FOREIGN KEY (codigo_a) REFERENCES Admin(codigo),
	CONSTRAINT fk_solicitud_libro FOREIGN KEY (ISBN) REFERENCES Libro(ISBN),
	CONSTRAINT chk_solicitud_estado CHECK (estado IN ('pendiente', 'aprobado', 'rechazado'))
);

CREATE TABLE Prestamo (
	idPrestamo VARCHAR(10) PRIMARY KEY,
	idSolicitud VARCHAR(10) NOT NULL UNIQUE,
	codigoBarras VARCHAR(20) NOT NULL,
	fechaPrestamo DATE NOT NULL,
	CONSTRAINT fk_prestamo_solicitud FOREIGN KEY (idSolicitud) REFERENCES SolicitudPrestamo(idSolicitud),
	CONSTRAINT fk_prestamo_ejemplar FOREIGN KEY (codigoBarras) REFERENCES Ejemplar(codigoBarras)
);

CREATE TABLE devolucion (
	idDevolucion VARCHAR(10) PRIMARY KEY,
	idPrestamo VARCHAR(10) NOT NULL UNIQUE,
	codigo VARCHAR(10) NOT NULL,
	fechaDevolucion DATE NOT NULL,
	observaciones VARCHAR(200) NOT NULL DEFAULT 'N/A',
	multa INT NOT NULL,
	CONSTRAINT fk_devolucion_prestamo FOREIGN KEY (idPrestamo) REFERENCES Prestamo(idPrestamo),
	CONSTRAINT fk_devolucion_admin FOREIGN KEY (codigo) REFERENCES Admin(codigo),
	CONSTRAINT chk_devolucion_multa CHECK (multa >= 0)
);

SELECT
	idSolicitud,
	fechaSolicitud,
	fechaSolicitud + 7 AS fechaVencimiento
FROM SolicitudPrestamo;