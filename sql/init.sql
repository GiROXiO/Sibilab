CREATE SCHEMA core;
SET search_path TO sibilab, core;

-- CATÁLOGO BASE (Entidades Independientes)

CREATE TABLE Editorial (
	idEditorial VARCHAR(10) PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL,
	CONSTRAINT chk_editorial_nombre CHECK (LENGTH(TRIM(nombre)) > 0),
	CONSTRAINT chk_editorial_id CHECK (idEditorial ~ 'ED\d{3}$')
);

CREATE TABLE Categoria (
	idCategoria VARCHAR(10) PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL,
	CONSTRAINT chk_categoria_nombre CHECK (LENGTH(TRIM(nombre)) > 0),
	CONSTRAINT chk_categoria_id CHECK (idCategoria ~ '^CAT\d{3}$')
);

CREATE TABLE Autor (
	idAutor VARCHAR(10) PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL,
	CONSTRAINT chk_autor_nombre CHECK (LENGTH(TRIM(nombre)) > 0),
	CONSTRAINT chk_autor_id CHECK (idAutor ~ '^AUT\d{3}$')
);

-- CATÁLOGO PRINCIPAL (Libros y Ejemplares)

CREATE TABLE Libro (
	ISBN VARCHAR(20) PRIMARY KEY,
	idEditorial VARCHAR(10) NOT NULL,
	titulo VARCHAR(100) NOT NULL,
	anio int NOT NULL,
	descripcion VARCHAR(1000),
	url_imagen VARCHAR(255),
	CONSTRAINT fk_libro_editorial FOREIGN KEY (idEditorial) REFERENCES Editorial(idEditorial),
	CONSTRAINT chk_libro_anio CHECK (anio > 1000 AND anio <= 2100),
	CONSTRAINT chk_libro_titulo CHECK (LENGTH(TRIM(titulo)) > 0),
	CONSTRAINT chk_libro_isbn CHECK (ISBN ~ '^\d{3}-\d{3}-\d{6}-\d{1}$')
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
	CONSTRAINT chk_ejemplar_estado CHECK (estado IN ('disponible', 'prestado', 'perdido', 'borrado')),
	CONSTRAINT chk_ejemplar_ubicacion CHECK (LENGTH(TRIM(ubicacion)) > 0),
	CONSTRAINT chk_ejemplar_id CHECK (codigoBarras ~ '^EJ\d{3}$')
);

-- USUARIOS Y HERENCIA

CREATE TABLE Usuario (
	codigo VARCHAR(10) PRIMARY KEY,
	identificacion VARCHAR(10) NOT NULL UNIQUE,
	nombre VARCHAR(60) NOT NULL,
	correo VARCHAR(100) NOT NULL UNIQUE,
	contrasenia VARCHAR(100) NOT NULL,
	CONSTRAINT chk_usuario_identificacion CHECK (LENGTH(TRIM(identificacion)) > 0),
	CONSTRAINT chk_usuario_nombre CHECK (LENGTH(TRIM(nombre)) > 0),
	CONSTRAINT chk_usuario_correo CHECK (correo LIKE '%@%.%'),
	CONSTRAINT chk_usuario_contrasenia CHECK (LENGTH(TRIM(contrasenia)) > 0),
	CONSTRAINT chk_usuario_codigo CHECK (codigo ~ '^\d{9}$')
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
	activo BOOLEAN NOT NULL DEFAULT TRUE,
	CONSTRAINT fk_admin_usuario FOREIGN KEY (codigo) REFERENCES Usuario(codigo)
);

-- PRESTAMOS Y DEVOLUCIONES

CREATE TABLE SolicitudPrestamo (
	idSolicitud VARCHAR(10) PRIMARY KEY,
	codigo_c VARCHAR(10) NOT NULL,
	codigo_a VARCHAR(10),
	ISBN VARCHAR(20) NOT NULL,
	estado VARCHAR(9) NOT NULL DEFAULT 'pendiente',
	CONSTRAINT fk_solicitud_cliente FOREIGN KEY (codigo_c) REFERENCES Cliente(codigo),
	CONSTRAINT fk_solicitud_admin FOREIGN KEY (codigo_a) REFERENCES Admin(codigo),
	CONSTRAINT fk_solicitud_libro FOREIGN KEY (ISBN) REFERENCES Libro(ISBN),
	CONSTRAINT chk_solicitud_estado CHECK (estado IN ('pendiente', 'aprobado', 'rechazado')),
	CONSTRAINT chk_solicitud_id CHECK (idSolicitud ~ '^SOL\d{3}$')
);

CREATE TABLE Prestamo (
	idPrestamo VARCHAR(10) PRIMARY KEY,
	idSolicitud VARCHAR(10) NOT NULL UNIQUE,
	codigoBarras VARCHAR(20) NOT NULL,
	fechaPrestamo DATE NOT NULL,
	fechaVencimiento Date NOT NULL,
	CONSTRAINT fk_prestamo_solicitud FOREIGN KEY (idSolicitud) REFERENCES SolicitudPrestamo(idSolicitud),
	CONSTRAINT fk_prestamo_ejemplar FOREIGN KEY (codigoBarras) REFERENCES Ejemplar(codigoBarras),
	CONSTRAINT chk_fechas_prestamo CHECK (fechaVencimiento >= fechaPrestamo),
	CONSTRAINT chk_prestamo_id CHECK (idPrestamo ~ '^PRE\d{3}$')
);

CREATE TABLE devolucion (
	idDevolucion VARCHAR(10) PRIMARY KEY,
	idPrestamo VARCHAR(10) NOT NULL UNIQUE,
	codigo VARCHAR(10) NOT NULL,
	fechaDevolucion DATE NOT NULL,
	observaciones VARCHAR(200) NOT NULL DEFAULT 'N/A',
	multa INT NOT NULL DEFAULT 0,
	pagado BOOLEAN NOT NULL DEFAULT FALSE,
	CONSTRAINT fk_devolucion_prestamo FOREIGN KEY (idPrestamo) REFERENCES Prestamo(idPrestamo),
	CONSTRAINT fk_devolucion_admin FOREIGN KEY (codigo) REFERENCES Admin(codigo),
	CONSTRAINT chk_devolucion_multa CHECK (multa >= 0),
	CONSTRAINT chk_devolucion_observaciones CHECK (LENGTH(TRIM(observaciones)) > 0),
	CONSTRAINT chk_devolucion_id CHECK (idDevolucion ~ '^DEV\d{3}$')
);