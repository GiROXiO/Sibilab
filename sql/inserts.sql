SET search_path TO sibilab, core;

INSERT INTO Editorial (idEditorial, nombre) VALUES
('ED001', 'Puello Academics'),
('ED002', 'Pearto'),
('ED003', 'TR0NKER COLLEGE'),
('ED004', 'Don Camarón DV'),
('ED005', 'Cocodrilo Ediciones'),
('ED006', 'GoogleEd'),
('ED007', 'Anaya'),
('ED008', 'Uninorte');


INSERT INTO Categoria (idCategoria, nombre) VALUES
('CAT001', 'Programación'),
('CAT002', 'Bases de Datos'),
('CAT003', 'Redes'),
('CAT004', 'Ingeniería de Software'),
('CAT005', 'Ciencia Ficción'),
('CAT006', 'Fantasía'),
('CAT007', 'Novela'),
('CAT008', 'Poesía'),
('CAT009', 'Historia'),
('CAT010', 'Filosofía'),
('CAT011', 'Ciencia'),
('CAT012', 'Psicología'),
('CAT013', 'Literatura Clásica'),
('CAT014', 'Literatura Infantil'),
('CAT015', 'Misterio y Suspenso'),
('CAT016', 'Cálculo'),
('CAT017', 'Finanzas'),
('CAT018', 'Política y Sociedad'),
('CAT019', 'Religión'),
('CAT020', 'Desarrollo Personal'),
('CAT021', 'Comunicación y Medios'),
('CAT022', 'Espiritualidad'),
('CAT023', 'Arte y Estética'),
('CAT024', 'Terror'),
('CAT025', 'Esoterismo'),
('CAT026', 'Aventura'),
('CAT027', 'Crimen y Sociedad'),
('CAT028', 'Antología'),
('CAT029', 'Biografía y Memorias'),
('CAT030', 'Informática y Teoría de la Información');


INSERT INTO Autor (idAutor, nombre) VALUES
('AUT000', 'Anonimo'),
('AUT001', 'Juan Cáceres'),
('AUT002', 'Miguel Carrizosa'),
('AUT003', 'Abelardo de la Espriella'),
('AUT004', 'Panchy Anon'),
('AUT005', 'Perón'),
('AUT006', 'Miguel de Cervantes Saavedra'),
('AUT007', 'Andrés Antonio S.'),
('AUT008', 'W. Y. Raquel'),
('AUT009', 'Dr. T'),
('AUT010', 'K. K. BIJOU'),
('AUT011', 'Vedolf'),
('AUT012', 'Jerónimo C.'),
('AUT013', 'Lebron J.'),
('AUT014', 'Santiago Vieira'),
('AUT015', 'Angelo de León'),
('AUT016', 'D. A. Marquez'),
('AUT017', 'Rashid Rodelo'),
('AUT018', 'Juan Guti'),
('AUT019', 'Andrés Saez');


-- TODOS LOS LIBROS ---------------------------------------------------------------------------
INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
	'123-670-000006-7', 
	'ED008', 
	'Tío rico, chaval pobre', 
	2026, 
	'¿Quién dijo que el éxito financiero requiere millones en el banco? En "Tío rico, chaval pobre", el joven y audaz estratega J. S. C. redefine las reglas del juego económico moderno. A través de una mezcla única de audacia, ingenio callejero y una total falta de complejos, este volumen nos adentra en las profundidades de la opulencia frugal.', 
	'/media/Libros/Tio rico, chaval pobre.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000002-1',
    'ED001',
    'Como ser muy atractivo para las chicas.',
    2024,
    'Una guía práctica y desenfadada sobre confianza personal, presentación, comunicación y habilidades sociales para desenvolverse con mayor seguridad en situaciones de interés romántico.',
    '/media/Libros/Como ser muy atractivo para las chicas.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000003-8',
    'ED007',
    'Don Quijote 2',
    2026,
    'Una continuación imaginaria de las aventuras de Don Quijote y Sancho Panza, en la que ambos emprenden nuevos viajes y se enfrentan a desafíos que pondrán a prueba su amistad, su ingenio y su particular manera de entender el mundo.',
    '/media/Libros/Don Quijote 2.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000004-2',
    'ED004',
    'El ahijado',
    2007,
    'En una tierra marcada por el honor y las antiguas tradiciones, un joven es llamado a asumir un destino que nunca eligió. Bajo la guía de quien lo considera su ahijado, deberá descubrir el significado de la lealtad, el legado y el valor que exige convertirse en el heredero de una historia que comenzó mucho antes de su nacimiento.',
    '/media/Libros/El Ahijado.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000005-7',
    'ED003',
    'El album del desastre de Hiroshima: Memorias de un testigo imaginario',
    1986,
    'Un relato ficticio presentado como las memorias de un testigo de la tragedia de Hiroshima. Entre recuerdos fragmentados y escenas surrealistas, el narrador reconstruye el instante de la explosión mientras contempla el hongo nuclear y las extrañas figuras que quedaron como testigos silenciosos de aquel día.',
    '/media/Libros/El album del desastre de Hiroshima.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000006-4',
    'ED005',
    'El Autor: Un relato de cayo gordo',
    2026,
    'Un relato surrealista ambientado en Cayo Gordo, donde una misteriosa figura de proporciones extraordinarias se convierte en el centro de una historia marcada por el humor, la extravagancia y las leyendas de un lugar aparentemente tranquilo. Entre encuentros inesperados y situaciones absurdas, el protagonista descubre que ser el autor de una historia puede ser mucho más extraño que vivirla.',
    '/media/Libros/El Autor.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000007-1',
    'ED006',
    'El invasor: 2 mundos, una amenaza',
    2013,
    'Cuando dos realidades comienzan a fusionarse, una presencia desconocida emerge desde el límite entre ambos mundos. Un extraño ser de rostro dividido se convierte en el símbolo de una amenaza que desafía toda lógica, mientras los habitantes de las dos dimensiones intentan descubrir quién es el invasor y qué busca en su mundo.',
    '/media/Libros/El Invasor.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000008-8',
    'ED001',
    'El precio del odiom.',
    2002,
    'Miguel A. Carrizosa se encuentra frente a uno de los acontecimientos más devastadores de la historia contemporánea. Entre el desconcierto, la tragedia y las preguntas que deja el atentado del 11 de septiembre, la historia explora el impacto del odio y las consecuencias que puede desencadenar mucho después de que el humo desaparece.',
    '/media/Libros/El precio del odiom.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000009-5',
    'ED002',
    'Embriagado de tu amor, Anastasia',
    2024,
    'Vedolf ha convertido el alcohol en refugio mientras intenta llenar el vacío que dejó Anastasia, su querida Anny. Su incapacidad para expresar sus sentimientos termina alejándola de su vida, obligándolo a enfrentarse a sus propios errores y a comprender, demasiado tarde, el precio de no haber sabido demostrar el amor que sentía.',
    '/media/Libros/Embriagado en tu amor, Anastasia.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000010-2',
    'ED002',
    'Enfermedades mentales modernas: Una historia en desarrollo',
    2020,
    'Una exploración de las enfermedades mentales que han cobrado relevancia en la sociedad contemporánea. El libro recorre sus posibles causas, manifestaciones y efectos en la vida cotidiana, mientras analiza cómo la comprensión de la salud mental ha evolucionado con el paso del tiempo.',
    '/media/Libros/Enfermedades mentales modernas.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000011-9',
    'ED001',
    'Fe Cristiana y el amor',
    2021,
    'Una reflexión sobre la relación entre la fe cristiana y el amor como principios fundamentales de la vida espiritual. A través de distintas experiencias y enseñanzas, la obra invita al lector a explorar cómo la compasión, el perdón y la entrega pueden transformar la manera en que nos relacionamos con los demás.',
    '/media/Libros/fe y cristianismo.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000012-6',
    'ED008',
    'Infantilización del medio moderno: Un ensayo sobre la cultura de la inmadurez',
    2026,
    'Un ensayo que analiza la creciente tendencia de la sociedad moderna hacia la búsqueda constante de entretenimiento, comodidad y gratificación inmediata. La obra reflexiona sobre cómo estas dinámicas pueden influir en la responsabilidad, la autonomía y la manera en que las personas enfrentan los desafíos de la vida adulta.',
    '/media/Libros/Infantilización del medio moderno.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000013-3',
    'ED006',
    'La derecha liberal: ensayo sobre el pensamiento político contemporáneo',
    2023,
    'Un ensayo que explora los principios de la derecha liberal y su evolución dentro del pensamiento político contemporáneo. La obra analiza conceptos como la libertad individual, la propiedad privada, el papel del Estado y la responsabilidad ciudadana, reflexionando sobre los debates que han marcado esta corriente política en las sociedades modernas.',
    '/media/Libros/La derecha liberal.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000014-0',
    'ED008',
    'La maestría del terrorismo',
    2004,
    'Un análisis sobre la influencia del miedo en los medios de comunicación modernos y su capacidad para moldear la percepción de la realidad. W. Y. Raquel examina cómo la difusión constante de acontecimientos violentos, amenazas y discursos de temor puede influir en la opinión pública y transformar la manera en que la sociedad interpreta los riesgos de su entorno.',
    '/media/Libros/La maestria del terrorismo.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000015-7',
    'ED002',
    'La muerte del Bodegón: Un ensayo surrealista',
    2015,
    'Un ensayo surrealista que explora la extraña desaparición de un bodegón y las preguntas que surgen alrededor de su ausencia. A través de imágenes, situaciones absurdas y reflexiones sobre el arte y la realidad, la obra cuestiona los límites entre lo cotidiano, lo imaginario y aquello que creemos comprender.',
    '/media/Libros/La muerte del Bodegon.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000016-4',
    'ED001',
    'Manual de sabiduría ancestral: Las rúnicas más importantes',
    2025,
    'Una introducción a las antiguas tradiciones rúnicas y al significado simbólico atribuido a sus principales signos. El libro presenta distintas interpretaciones de las runas y reflexiona sobre su relación con la sabiduría, la espiritualidad y las prácticas culturales de los pueblos que las utilizaron.',
    '/media/Libros/Las runicas mas importantes.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000017-1',
    'ED008',
    'Llamada sagrada a una utopía imposible',
    2026,
    'Una obra de reflexión filosófica que explora la búsqueda de una sociedad ideal y las contradicciones que aparecen cuando los seres humanos intentan convertir sus ideales en realidad. A través de una llamada simbólica hacia un futuro aparentemente perfecto, el autor cuestiona los límites entre la esperanza, la fe y la imposibilidad de alcanzar una utopía definitiva.',
    '/media/Libros/Llamada sagrada.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000018-8',
    'ED002',
    'Mi amiga la roca',
    2023,
    'Una historia fantástica sobre una joven que descubre una misteriosa roca con la capacidad de guardar recuerdos y secretos de un antiguo mundo olvidado. A medida que su vínculo con ella se fortalece, ambas emprenden un viaje a través de paisajes extraordinarios, criaturas desconocidas y ruinas que esconden una historia mucho más antigua de lo que podían imaginar.',
    '/media/Libros/Mi amiga la roca.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000019-5',
    'ED001',
    'Mi Pesca',
    2026,
    'Una obra que combina una historia de pesca con conceptos relacionados con la teoría de códigos. Rashid Rodelo presenta una perspectiva particular en la que la búsqueda de una buena pesca se convierte en una exploración de patrones, señales y formas de interpretar la información, demostrando que incluso una actividad aparentemente sencilla puede esconder estructuras y estrategias complejas.',
    '/media/Libros/Mi Pesca.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000020-2',
    'ED005',
    'Mi primer pepazo: Memorias desde los márgenes del crimen organizado',
    2019,
    'Una narración de carácter autobiográfico que reconstruye las experiencias de un personaje que crece en medio de un entorno marcado por la violencia, la ilegalidad y las difíciles decisiones del mundo del crimen organizado. A través de recuerdos, conflictos y momentos de tensión, la obra reflexiona sobre las consecuencias de crecer en los márgenes de una sociedad atravesada por estas dinámicas.',
    '/media/Libros/Mi primer pepazo.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000021-9',
    'ED003',
    '30 grandes éxitos y los mejores poemas',
    2024,
    'Una recopilación de los treinta grandes éxitos literarios de Miguel Carrizosa, acompañados por una selección de sus poemas más representativos. La obra reúne diferentes momentos de su trayectoria como escritor, explorando temas como el amor, la nostalgia, las experiencias cotidianas y las reflexiones sobre la vida.',
    '/media/Libros/Miguel grandes exitos.jpeg'
);


INSERT INTO Libro (ISBN, idEditorial, titulo, anio, descripcion, url_imagen) VALUES
(
    '978-000-000022-6',
    'ED002',
    'Soledad Mental',
    2017,
    'Una obra del Dr. T. que explora la experiencia de la soledad desde una perspectiva psicológica y reflexiva. El autor analiza cómo el aislamiento emocional, la dificultad para establecer vínculos y los pensamientos recurrentes pueden influir en la percepción que una persona tiene de sí misma y de su entorno.',
    '/media/Libros/Soledad Mental.jpeg'
);


-- TODOS LOS LIBROS ---------------------------------------------------------------------------

-- CATEGORIAS + LIBRO
INSERT INTO Pertenece (ISBN, idCategoria) VALUES
('123-670-000006-7', 'CAT017'),
('123-670-000006-7', 'CAT007'),
('978-000-000002-1', 'CAT020'),
('978-000-000002-1', 'CAT012'),
('978-000-000003-8', 'CAT007'),
('978-000-000003-8', 'CAT013'),
('978-000-000004-2', 'CAT007'),
('978-000-000004-2', 'CAT006'),
('978-000-000005-7', 'CAT009'),
('978-000-000005-7', 'CAT007'),
('978-000-000006-4', 'CAT007'),
('978-000-000006-4', 'CAT006'),
('978-000-000007-1', 'CAT005'),
('978-000-000007-1', 'CAT006'),
('978-000-000008-8', 'CAT009'),
('978-000-000008-8', 'CAT018'),
('978-000-000009-5', 'CAT007'),
('978-000-000009-5', 'CAT020'),
('978-000-000010-2', 'CAT012'),
('978-000-000010-2', 'CAT011'),
('978-000-000011-9', 'CAT019'),
('978-000-000011-9', 'CAT022'),
('978-000-000012-6', 'CAT018'),
('978-000-000012-6', 'CAT012'),
('978-000-000013-3', 'CAT018'),
('978-000-000013-3', 'CAT010'),
('978-000-000014-0', 'CAT021'),
('978-000-000014-0', 'CAT018'),
('978-000-000014-0', 'CAT024'),
('978-000-000015-7', 'CAT023'),
('978-000-000015-7', 'CAT010'),
('978-000-000016-4', 'CAT025'),
('978-000-000016-4', 'CAT022'),
('978-000-000016-4', 'CAT009'),
('978-000-000017-1', 'CAT010'),
('978-000-000017-1', 'CAT022'),
('978-000-000017-1', 'CAT018'),
('978-000-000018-8', 'CAT006'),
('978-000-000018-8', 'CAT026'),
('978-000-000019-5', 'CAT011'),
('978-000-000019-5', 'CAT030'),
('978-000-000020-2', 'CAT027'),
('978-000-000020-2', 'CAT007'),
('978-000-000021-9', 'CAT008'),
('978-000-000021-9', 'CAT028'),
('978-000-000022-6', 'CAT012'),
('978-000-000022-6', 'CAT007');



-- AUTOR + LIBRO
INSERT INTO Escribe (ISBN, idAutor) VALUES
('123-670-000006-7', 'AUT001'),
('978-000-000002-1', 'AUT015'),
('978-000-000003-8', 'AUT006'),
('978-000-000004-2', 'AUT014'),
('978-000-000005-7', 'AUT004'),
('978-000-000006-4', 'AUT013'),
('978-000-000007-1', 'AUT019'),
('978-000-000008-8', 'AUT002'),
('978-000-000009-5', 'AUT011'),
('978-000-000010-2', 'AUT005'),
('978-000-000011-9', 'AUT002'),
('978-000-000012-6', 'AUT008'),
('978-000-000013-3', 'AUT018'),
('978-000-000014-0', 'AUT008'),
('978-000-000015-7', 'AUT005'),
('978-000-000016-4', 'AUT016'),
('978-000-000017-1', 'AUT012'),
('978-000-000018-8', 'AUT010'),
('978-000-000019-5', 'AUT017'),
('978-000-000020-2', 'AUT000'),
('978-000-000021-9', 'AUT002'),
('978-000-000022-6', 'AUT009');


-- EJEMPLARES
INSERT INTO Ejemplar (codigoBarras, ISBN, ubicacion, estado) VALUES
('EJ001', '123-670-000006-7', 'A01', 'disponible'),
('EJ002', '123-670-000006-7', 'A01', 'disponible'),
('EJ003', '123-670-000006-7', 'A01', 'disponible'),
('EJ004', '978-000-000002-1', 'A02', 'disponible'),
('EJ005', '978-000-000002-1', 'A02', 'disponible'),
('EJ006', '978-000-000002-1', 'A02', 'disponible'),
('EJ007', '978-000-000003-8', 'A03', 'disponible'),
('EJ008', '978-000-000003-8', 'A03', 'disponible'),
('EJ009', '978-000-000003-8', 'A03', 'disponible'),
('EJ010', '978-000-000004-2', 'A04', 'disponible'),
('EJ011', '978-000-000004-2', 'A04', 'disponible'),
('EJ012', '978-000-000004-2', 'A04', 'disponible'),
('EJ013', '978-000-000005-7', 'A05', 'disponible'),
('EJ014', '978-000-000005-7', 'A05', 'disponible'),
('EJ015', '978-000-000005-7', 'A05', 'disponible'),
('EJ016', '978-000-000006-4', 'A06', 'disponible'),
('EJ017', '978-000-000006-4', 'A06', 'disponible'),
('EJ018', '978-000-000006-4', 'A06', 'disponible'),
('EJ019', '978-000-000007-1', 'A07', 'prestado'),
('EJ020', '978-000-000007-1', 'A07', 'disponible'),
('EJ021', '978-000-000007-1', 'A07', 'disponible'),
('EJ022', '978-000-000008-8', 'A08', 'disponible'),
('EJ023', '978-000-000008-8', 'A08', 'disponible'),
('EJ024', '978-000-000008-8', 'A08', 'disponible'),
('EJ025', '978-000-000009-5', 'A09', 'disponible'),
('EJ026', '978-000-000009-5', 'A09', 'disponible'),
('EJ027', '978-000-000009-5', 'A09', 'disponible'),
('EJ028', '978-000-000010-2', 'A10', 'disponible'),
('EJ029', '978-000-000010-2', 'A10', 'disponible'),
('EJ030', '978-000-000010-2', 'A10', 'disponible'),
('EJ031', '978-000-000011-9', 'A11', 'disponible'),
('EJ032', '978-000-000011-9', 'A11', 'disponible'),
('EJ033', '978-000-000011-9', 'A11', 'disponible'),
('EJ034', '978-000-000012-6', 'A12', 'disponible'),
('EJ035', '978-000-000012-6', 'A12', 'disponible'),
('EJ036', '978-000-000012-6', 'A12', 'disponible'),
('EJ037', '978-000-000013-3', 'A13', 'disponible'),
('EJ038', '978-000-000013-3', 'A13', 'disponible'),
('EJ039', '978-000-000013-3', 'A13', 'disponible'),
('EJ040', '978-000-000014-0', 'A14', 'disponible'),
('EJ041', '978-000-000014-0', 'A14', 'disponible'),
('EJ042', '978-000-000014-0', 'A14', 'disponible'),
('EJ043', '978-000-000015-7', 'A15', 'disponible'),
('EJ044', '978-000-000015-7', 'A15', 'disponible'),
('EJ045', '978-000-000015-7', 'A15', 'disponible'),
('EJ046', '978-000-000016-4', 'A16', 'disponible'),
('EJ047', '978-000-000016-4', 'A16', 'disponible'),
('EJ048', '978-000-000016-4', 'A16', 'disponible'),
('EJ049', '978-000-000017-1', 'A17', 'disponible'),
('EJ050', '978-000-000017-1', 'A17', 'disponible'),
('EJ051', '978-000-000017-1', 'A17', 'disponible'),
('EJ052', '978-000-000018-8', 'A18', 'disponible'),
('EJ053', '978-000-000018-8', 'A18', 'disponible'),
('EJ054', '978-000-000018-8', 'A18', 'disponible'),
('EJ055', '978-000-000019-5', 'A19', 'disponible'),
('EJ056', '978-000-000019-5', 'A19', 'disponible'),
('EJ057', '978-000-000019-5', 'A19', 'disponible'),
('EJ058', '978-000-000020-2', 'A20', 'prestado'),
('EJ059', '978-000-000020-2', 'A20', 'disponible'),
('EJ060', '978-000-000020-2', 'A20', 'disponible'),
('EJ061', '978-000-000021-9', 'A21', 'disponible'),
('EJ062', '978-000-000021-9', 'A21', 'disponible'),
('EJ063', '978-000-000021-9', 'A21', 'disponible'),
('EJ064', '978-000-000022-6', 'A22', 'prestado'),
('EJ065', '978-000-000022-6', 'A22', 'disponible'),
('EJ066', '978-000-000022-6', 'A22', 'disponible');



-- Usuarios
INSERT INTO Usuario (codigo, identificacion, nombre, correo, contrasenia) VALUES
('204593812', '1000000001', 'Carlos Rodríguez', 'carlos.rodriguez@sibilab.com', 'Sibi1234'),
('219847365', '1000000002', 'Mariana López', 'mariana.lopez@sibilab.com', 'Sibi1234'),
('258392014', '1000000003', 'Andrés Martínez', 'andres.martinez@sibilab.com', 'Sibi1234'),
('283746192', '1000000004', 'Laura Gómez', 'laura.gomez@sibilab.com', 'Sibi1234'),
('231094857', '1000000005', 'Santiago Pérez', 'santiago.perez@sibilab.com', 'Sibi1234'),
('294857103', '1000000006', 'Valentina Torres', 'valentina.torres@sibilab.com', 'Sibi1234'),
('247103958', '1000000007', 'Daniel Hernández', 'daniel.hernandez@sibilab.com', 'Sibi1234'),
('265839104', '1000000008', 'Camila Vargas', 'camila.vargas@sibilab.com', 'Sibi1234'),
('210495837', '1000000009', 'Mateo Castillo', 'mateo.castillo@sibilab.com', 'Sibi1234'),
('273849102', '1000000010', 'Sofía Ramírez', 'sofia.ramirez@sibilab.com', 'Sibi1234'),
('228394015', '1000000011', 'Samuel Puello', 'samuel.puello@sibilab.com', 'Sibi1234'),
('289102374', '1000000012', 'Oreste de León', 'oreste.deleon@sibilab.com', 'Sibi1234'),
('256738190', '1000000013', 'Andrés Saez', 'andres.saez@sibilab.com', 'Sibi1234'),
('214958302', '1000000014', 'Alejandro Chaves', 'alejandro.chaves@sibilab.com', 'Sibi1234'),

('200192837', '1000000015', 'Juan Cáceres', 'jscaceres@uninorte.edu.co', 'contraseña1'),
('200384756', '1000000016', 'Miguel Carrizosa', 'carrizosam@uninorte.edu.co', 'contraseña2'),
('200574839', '1000000017', 'Juan Arrieta', 'coleyf@uninorte.edu.co', 'contraseña3'),
('200485920', '1000000018', 'Jerónimo Castro', 'jeronimoac@uninorte.edu.co', 'contraseña4');


INSERT INTO Admin (codigo) VALUES
('200192837'),
('200384756'),
('200574839'),
('200485920');


INSERT INTO Cliente (codigo, rol, carrera, estado) VALUES
('204593812', 'estudiante', 'Ingeniería de Sistemas', 'activo'),
('219847365', 'estudiante', 'Ingeniería Industrial', 'activo'),
('258392014', 'docente', NULL, 'activo'),
('283746192', 'estudiante', 'Derecho', 'activo'),
('231094857', 'estudiante', 'Ingeniería de Sistemas', 'activo'),
('294857103', 'docente', NULL, 'activo'),
('247103958', 'estudiante', 'Administración de Empresas', 'activo'),
('265839104', 'estudiante', 'Psicología', 'activo'),
('210495837', 'docente', NULL, 'activo'),
('273849102', 'estudiante', 'Ingeniería Electrónica', 'activo'),
('228394015', 'estudiante', 'Ingeniería de Sistemas', 'activo'),
('289102374', 'docente', NULL, 'activo'),
('256738190', 'estudiante', 'Ingeniería de Sistemas', 'activo'),
('214958302', 'estudiante', 'Ingeniería de Sistemas', 'activo');


-- Solicitudes y prestamos
INSERT INTO SolicitudPrestamo (idSolicitud, codigo_c, codigo_a, ISBN, estado) VALUES
('SOL001', '204593812', NULL, '123-670-000006-7', 'pendiente'),
('SOL002', '219847365', '200192837', '978-000-000003-8', 'aprobado'),
('SOL003', '258392014', '200384756', '978-000-000010-2', 'rechazado'),
('SOL004', '283746192', NULL, '978-000-000018-8', 'pendiente'),
('SOL005', '231094857', '200574839', '978-000-000019-5', 'aprobado'),
('SOL006', '294857103', '200485920', '978-000-000014-0', 'rechazado'),
('SOL007', '247103958', NULL, '978-000-000021-9', 'pendiente'),
('SOL008', '265839104', '200192837', '978-000-000011-9', 'aprobado'),
('SOL009', '210495837', NULL, '978-000-000013-3', 'pendiente'),
('SOL010', '273849102', '200384756', '978-000-000022-6', 'aprobado'),
('SOL011', '228394015', '200574839', '978-000-000006-4', 'rechazado'),
('SOL012', '289102374', NULL, '978-000-000016-4', 'pendiente'),
('SOL013', '256738190', '200485920', '978-000-000007-1', 'aprobado'),
('SOL014', '214958302', NULL, '978-000-000004-2', 'pendiente'),
('SOL015', '204593812', '200192837', '978-000-000020-2', 'aprobado'),
('SOL016', '283746192', '200485920', '123-670-000006-7', 'aprobado'),
('SOL017', '247103958', '200192837', '978-000-000004-2', 'aprobado'),
('SOL018', '265839104', '200384756', '978-000-000012-6', 'aprobado'),
('SOL019', '210495837', '200574839', '978-000-000017-1', 'aprobado'),
('SOL020', '228394015', NULL, '978-000-000019-5', 'pendiente'),
('SOL021', '289102374', '200485920', '978-000-000008-8', 'rechazado'),
('SOL022', '214958302', '200192837', '978-000-000015-7', 'aprobado'),
('SOL023', '204593812', '200192837', '978-000-000005-7', 'aprobado'),
('SOL024', '219847365', '200384756', '978-000-000009-5', 'aprobado'),
('SOL025', '258392014', '200574839', '978-000-000010-2', 'aprobado'),
('SOL026', '283746192', '200485920', '978-000-000012-6', 'aprobado'),
('SOL027', '231094857', '200192837', '978-000-000015-7', 'aprobado'),
('SOL028', '294857103', '200384756', '978-000-000017-1', 'aprobado'),
('SOL029', '247103958', '200574839', '978-000-000021-9', 'aprobado'),
('SOL030', '265839104', '200485920', '978-000-000022-6', 'aprobado'),
('SOL031', '210495837', '200192837', '123-670-000006-7', 'aprobado'),
('SOL032', '273849102', '200384756', '978-000-000002-1', 'aprobado'),
('SOL033', '228394015', '200574839', '978-000-000003-8', 'aprobado'),
('SOL034', '289102374', '200485920', '978-000-000006-4', 'aprobado'),
('SOL035', '256738190', '200192837', '978-000-000007-1', 'aprobado'),
('SOL036', '214958302', '200384756', '978-000-000008-8', 'aprobado'),
('SOL037', '204593812', '200574839', '978-000-000011-9', 'aprobado'),
('SOL038', '219847365', '200485920', '978-000-000013-3', 'aprobado'),
('SOL039', '258392014', '200192837', '978-000-000014-0', 'aprobado'),
('SOL040', '283746192', '200384756', '978-000-000016-4', 'aprobado'),
('SOL041', '231094857', '200574839', '978-000-000018-8', 'aprobado'),
('SOL042', '294857103', '200485920', '978-000-000019-5', 'aprobado'),
('SOL043', '247103958', '200192837', '978-000-000020-2', 'rechazado'),
('SOL044', '265839104', '200384756', '978-000-000005-7', 'rechazado'),
('SOL045', '210495837', '200574839', '978-000-000009-5', 'rechazado'),
('SOL046', '273849102', '200485920', '978-000-000010-2', 'rechazado'),
('SOL047', '228394015', NULL, '978-000-000012-6', 'pendiente'),
('SOL048', '289102374', NULL, '978-000-000015-7', 'pendiente'),
('SOL049', '256738190', NULL, '978-000-000017-1', 'pendiente'),
('SOL050', '214958302', NULL, '978-000-000021-9', 'pendiente'),
('SOL051', '204593812', '200192837', '978-000-000022-6', 'rechazado'),
('SOL052', '219847365', NULL, '123-670-000006-7', 'pendiente');

INSERT INTO Prestamo (idPrestamo, idSolicitud, codigoBarras, fechaPrestamo, fechaVencimiento) VALUES
('PRE001', 'SOL002', 'EJ007', '2026-10-01', '2026-10-08'),
('PRE002', 'SOL005', 'EJ055', '2026-10-01', '2026-10-08'),
('PRE003', 'SOL008', 'EJ031', '2026-10-01', '2026-10-08'),
('PRE004', 'SOL010', 'EJ064', '2026-10-01', '2026-10-08'),
('PRE005', 'SOL013', 'EJ019', '2026-10-01', '2026-10-08'),
('PRE006', 'SOL015', 'EJ058', '2026-10-01', '2026-10-08'),
('PRE007', 'SOL016', 'EJ001', '2026-08-01', '2026-08-08'),
('PRE008', 'SOL017', 'EJ010', '2026-08-15', '2026-08-22'),
('PRE009', 'SOL018', 'EJ034', '2026-09-02', '2026-09-09'),
('PRE010', 'SOL019', 'EJ049', '2026-09-20', '2026-09-27'),
('PRE011', 'SOL022', 'EJ043', '2026-10-10', '2026-10-17'),
('PRE012', 'SOL023', 'EJ013', '2026-03-05', '2026-03-12'),
('PRE013', 'SOL024', 'EJ025', '2026-03-15', '2026-03-22'),
('PRE014', 'SOL025', 'EJ028', '2026-04-10', '2026-04-17'),
('PRE015', 'SOL026', 'EJ035', '2026-04-22', '2026-04-29'),
('PRE016', 'SOL027', 'EJ044', '2026-05-02', '2026-05-09'),
('PRE017', 'SOL028', 'EJ050', '2026-05-18', '2026-05-25'),
('PRE018', 'SOL029', 'EJ061', '2026-06-05', '2026-06-12'),
('PRE019', 'SOL030', 'EJ065', '2026-06-20', '2026-06-27'),
('PRE020', 'SOL031', 'EJ002', '2026-07-08', '2026-07-15'),
('PRE021', 'SOL032', 'EJ004', '2026-07-25', '2026-08-01'),
('PRE022', 'SOL033', 'EJ008', '2026-08-12', '2026-08-19'),
('PRE023', 'SOL034', 'EJ016', '2026-08-28', '2026-09-04'),
('PRE024', 'SOL035', 'EJ020', '2026-09-05', '2026-09-12'),
('PRE025', 'SOL036', 'EJ022', '2026-09-18', '2026-09-25'),
('PRE026', 'SOL037', 'EJ032', '2026-10-02', '2026-10-09'),
('PRE027', 'SOL038', 'EJ037', '2026-10-05', '2026-10-12'),
('PRE028', 'SOL039', 'EJ040', '2026-10-12', '2026-10-19'),
('PRE029', 'SOL040', 'EJ046', '2026-10-14', '2026-10-21'),
('PRE030', 'SOL041', 'EJ052', '2026-10-16', '2026-10-23'),
('PRE031', 'SOL042', 'EJ056', '2026-10-18', '2026-10-25');


-- Devoluciones 
INSERT INTO Devolucion (idDevolucion, idPrestamo, codigo, fechaDevolucion, observaciones, multa, pagado) VALUES
('DEV001', 'PRE001', '200192837', '2026-10-07', 'Devuelto en buen estado', 0, TRUE),
('DEV002', 'PRE002', '200384756', '2026-10-08', 'Devuelto en buen estado', 0, FALSE),
('DEV003', 'PRE003', '200574839', '2026-10-08', 'Presenta algunas marcas de uso', 5000, FALSE),
('DEV004', 'PRE007', '200485920', '2026-08-08', 'Libro en perfectas condiciones', 0, TRUE),
('DEV005', 'PRE008', '200192837', '2026-08-25', 'El estudiante reportó un retraso por enfermedad', 15000, TRUE),
('DEV006', 'PRE009', '200384756', '2026-09-15', 'Se entregó con la portada doblada y fuera de fecha', 30000, FALSE),
('DEV007', 'PRE010', '200574839', '2026-09-26', 'Devuelto antes de tiempo', 0, TRUE),
('DEV008', 'PRE012', '200192837', '2026-03-10', 'Devuelto sin problemas', 0, TRUE),
('DEV009', 'PRE013', '200384756', '2026-03-22', 'Devolución estándar', 0, TRUE),
('DEV010', 'PRE014', '200574839', '2026-04-16', 'Excelente estado', 0, TRUE),
('DEV011', 'PRE015', '200485920', '2026-05-02', '3 días de retraso', 15000, TRUE),
('DEV012', 'PRE016', '200192837', '2026-05-12', 'Libro entregado tarde, multa cobrada en caja', 15000, TRUE),
('DEV013', 'PRE017', '200384756', '2026-06-15', 'Entregado con 21 días de retraso. Hojas rayadas.', 105000, FALSE),
('DEV014', 'PRE018', '200574839', '2026-07-02', 'El estudiante lo trajo mucho después, deuda activa', 100000, FALSE),
('DEV015', 'PRE019', '200485920', '2026-07-15', 'Retraso de 18 días, el usuario no tenía dinero para pagar', 90000, FALSE),
('DEV016', 'PRE020', '200192837', '2026-07-14', 'Devolución normal', 0, TRUE),
('DEV017', 'PRE021', '200384756', '2026-08-01', 'Normal', 0, TRUE),
('DEV018', 'PRE022', '200574839', '2026-08-25', 'Retraso moderado, no ha pagado', 30000, FALSE),
('DEV019', 'PRE023', '200485920', '2026-09-02', 'Devuelto a tiempo', 0, TRUE),
('DEV020', 'PRE024', '200192837', '2026-09-10', 'A tiempo', 0, TRUE),
('DEV021', 'PRE025', '200384756', '2026-09-26', '1 día tarde', 5000, FALSE),
('DEV022', 'PRE026', '200574839', '2026-10-09', 'Ligeramente mojado, se cobró multa por daño', 25000, TRUE);