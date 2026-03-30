CREATE DATABASE IF NOT EXISTS almacor_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE almacor_db;

-- Roles de usuario
CREATE TABLE IF NOT EXISTS roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Usuarios del sistema
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  usuario VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol_id INT NOT NULL,
  estado ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  ultimo_acceso DATETIME NULL,
  FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- Productos / Inventario
CREATE TABLE IF NOT EXISTS productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  referencia VARCHAR(30) NOT NULL UNIQUE,
  nombre VARCHAR(150) NOT NULL,
  talla VARCHAR(30) NOT NULL,
  color VARCHAR(40) NOT NULL,
  stock_actual INT NOT NULL DEFAULT 0,
  stock_minimo INT NOT NULL DEFAULT 5,
  ubicacion VARCHAR(120) NULL,
  precio DECIMAL(10,2) NOT NULL DEFAULT 0.0
);

-- Ventas (cabecera)
CREATE TABLE IF NOT EXISTS ventas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(30) NOT NULL UNIQUE,
  fecha DATETIME NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  descuento DECIMAL(10,2) NOT NULL DEFAULT 0.0,
  estado ENUM('COMPLETADA','CANCELADA','ENVIANDO') NOT NULL DEFAULT 'COMPLETADA',
  cliente VARCHAR(150) NULL,
  vendedor_id INT NOT NULL,
  notas TEXT NULL,
  FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
);

-- Detalle de ventas (FIX: producto_id NULLABLE + ON DELETE SET NULL)
CREATE TABLE IF NOT EXISTS ventas_detalle (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venta_id INT NOT NULL,
  producto_id INT NULL,
  talla VARCHAR(30) NOT NULL,
  cantidad INT NOT NULL,
  precio_unit DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
);

-- Envíos
CREATE TABLE IF NOT EXISTS envios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  guia VARCHAR(40) NOT NULL UNIQUE,
  fecha DATETIME NOT NULL,
  producto_descripcion VARCHAR(200) NOT NULL,
  cliente VARCHAR(150) NOT NULL,
  ciudad_destino VARCHAR(100) NOT NULL,
  direccion TEXT NOT NULL,
  estado ENUM('EN_TRANSITO','ENTREGADO','PENDIENTE','CANCELADO') NOT NULL DEFAULT 'EN_TRANSITO',
  vendedor_id INT NOT NULL,
  FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
);

-- Datos iniciales
INSERT IGNORE INTO roles (id, nombre) VALUES
  (1, 'ADMIN'),
  (2, 'EMPLEADO');

-- Usuarios de prueba con contraseñas en PLAIN TEXT (INSECURE - solo desarrollo)
-- user/password pairs:
-- admin/admin123, juanp/pass123, mariacl/pass456, etc.

INSERT INTO usuarios (nombre, usuario, password_hash, rol_id, estado, ultimo_acceso) VALUES
('Admin Principal', 'admin', 'admin123', 1, 'ACTIVO', '2024-10-01 10:00:00'),
('Juan Pérez', 'juanp', 'pass123', 2, 'ACTIVO', '2024-10-02 11:30:00'),
('María López', 'mariacl', 'pass456', 2, 'ACTIVO', '2024-10-03 14:20:00'),
('Carlos García', 'carlosg', 'pass789', 2, 'ACTIVO', '2024-10-04 09:15:00'),
('Ana Rodríguez', 'anar', 'passabc', 1, 'ACTIVO', '2024-10-05 16:45:00'),
('Luis Martínez', 'luism', 'passdef', 2, 'INACTIVO', '2024-10-06 12:10:00'),
('Sofía Hernández', 'sofiah', 'passghi', 2, 'ACTIVO', NULL),
('Diego Sánchez', 'diegos', 'passjkl', 1, 'ACTIVO', '2024-10-08 13:25:00'),
('Laura Torres', 'laurat', 'passmno', 2, 'ACTIVO', '2024-10-09 10:50:00'),
('Miguel Ramírez', 'miguelr', 'passpqr', 2, 'ACTIVO', '2024-10-10 15:30:00'),
('Elena Vargas', 'elenav', 'passstu', 1, 'ACTIVO', NULL),
('Pedro Castillo', 'pedroc', 'passvwx', 2, 'ACTIVO', '2024-10-12 11:00:00');

-- 20 Productos
INSERT INTO productos (referencia, nombre, talla, color, stock_actual, stock_minimo, ubicacion, precio) VALUES
('REF001', 'Camiseta Nike Air', 'M', 'Negro', 25, 5, 'A-01', 29.99),
('REF002', 'Pantalón Adidas', 'L', 'Azul', 12, 3, 'B-05', 49.99),
('REF003', 'Zapatillas Puma', '42', 'Blanco', 8, 2, 'C-10', 79.99),
('REF004', 'Sudadera Under Armour', 'S', 'Gris', 35, 10, 'A-02', 59.99),
('REF005', 'Camiseta Polo Ralph Lauren', 'XL', 'Blanco', 18, 5, 'B-01', 39.99),
('REF006', 'Jeans Levi\'s', '32', 'Azul oscuro', 22, 7, 'B-06', 69.99),
('REF007', 'Botas Timberland', '41', 'Marrón', 5, 1, 'C-11', 129.99),
('REF008', 'Chaqueta North Face', 'M', 'Rojo', 15, 4, 'A-03', 199.99),
('REF009', 'Calcetines Nike', '42-44', 'Negro/Blanco', 100, 20, 'D-01', 9.99),
('REF010', 'Gorra New Era', 'M', 'Negro', 40, 10, 'E-01', 24.99),
('REF011', 'Camiseta Manchester United', 'L', 'Rojo', 30, 8, 'A-04', 34.99),
('REF012', 'Shorts Nike', 'M', 'Gris', 28, 6, 'B-07', 29.99),
('REF013', 'Sandalias Crocs', '40', 'Azul', 45, 12, 'C-12', 44.99),
('REF014', 'Abrigo Zara', 'S', 'Negro', 10, 3, 'A-05', 89.99),
('REF015', 'Reloj Casio', 'Uni', 'Plata', 16, 5, 'F-01', 59.99),
('REF016', 'Mochila Herschel', 'Uni', 'Gris', 20, 5, 'G-01', 79.99),
('REF017', 'Polera H&M', 'XL', 'Verde', 32, 9, 'B-08', 25.99),
('REF018', 'Converse Chuck', '39', 'Blanco', 14, 4, 'C-13', 64.99),
('REF019', 'Bufanda Burberry', 'Uni', 'Beige', 50, 15, 'H-01', 149.99),
('REF020', 'Guantes Under Armour', 'L', 'Negro', 60, 18, 'D-02', 19.99);

-- 12 Ventas (vendedor_id 1-6)
INSERT INTO ventas (codigo, fecha, total, descuento, estado, cliente, vendedor_id, notas) VALUES
('VEN001', '2024-10-15 10:30:00', 129.98, 10.00, 'COMPLETADA', 'Cliente A', 1, 'Venta rápida'),
('VEN002', '2024-10-15 11:45:00', 89.98, 0.00, 'COMPLETADA', 'Cliente B', 2, NULL),
('VEN003', '2024-10-15 14:20:00', 199.97, 20.00, 'ENVIANDO', 'Cliente C', 3, 'Urgente'),
('VEN004', '2024-10-15 16:10:00', 59.98, 5.00, 'COMPLETADA', 'Cliente D', 4, NULL),
('VEN005', '2024-10-16 09:25:00', 249.96, 15.00, 'CANCELADA', 'Cliente E', 5, 'Cliente canceló'),
('VEN006', '2024-10-16 12:50:00', 79.97, 0.00, 'COMPLETADA', 'Cliente F', 6, NULL),
('VEN007', '2024-10-16 15:35:00', 149.95, 10.00, 'COMPLETADA', 'Cliente G', 1, 'Paquete regalo'),
('VEN008', '2024-10-17 10:15:00', 44.98, 5.00, 'ENVIANDO', 'Cliente H', 2, NULL),
('VEN009', '2024-10-17 13:40:00', 299.94, 25.00, 'COMPLETADA', 'Cliente I', 3, 'Mayorista'),
('VEN010', '2024-10-17 17:20:00', 69.97, 0.00, 'COMPLETADA', 'Cliente J', 4, NULL),
('VEN011', '2024-10-18 11:05:00', 109.96, 10.00, 'ENVIANDO', 'Cliente K', 5, NULL),
('VEN012', '2024-10-18 14:55:00', 94.95, 5.00, 'COMPLETADA', 'Cliente L', 6, 'Satisfecho');

-- 12 Envíos
INSERT INTO envios (guia, fecha, producto_descripcion, cliente, ciudad_destino, direccion, estado, vendedor_id) VALUES
('GUIA001', '2024-10-15 12:00:00', 'Camiseta Nike Air + Zapatillas', 'Cliente A', 'Bogotá', 'Calle 100 #20-30, Apt 401', 'ENTREGADO', 1),
('GUIA002', '2024-10-15 13:15:00', 'Pantalón Adidas + Sudadera', 'Cliente B', 'Medellín', 'Carrera 50 #45-67', 'EN_TRANSITO', 2),
('GUIA003', '2024-10-15 15:40:00', 'Chaqueta North Face', 'Cliente C', 'Cali', 'Av 6N #23-85', 'PENDIENTE', 3),
('GUIA004', '2024-10-15 17:25:00', 'Camiseta Polo + Calcetines', 'Cliente D', 'Barranquilla', 'Calle 84 #52-10', 'ENTREGADO', 4),
('GUIA005', '2024-10-16 10:40:00', 'Botas Timberland + Reloj', 'Cliente E', 'Bucaramanga', 'Carrera 28 #39-20', 'CANCELADO', 5),
('GUIA006', '2024-10-16 14:05:00', 'Mochila Herschel', 'Cliente F', 'Pereira', 'Calle 25 #7-50', 'ENTREGADO', 6),
('GUIA007', '2024-10-16 16:50:00', 'Camiseta ManU + Shorts', 'Cliente G', 'Manizales', 'Av Santander #12-30', 'ENTREGADO', 1),
('GUIA008', '2024-10-17 11:30:00', 'Gorra New Era + Polera', 'Cliente H', 'Cartagena', 'Calle 32 #15-80', 'EN_TRANSITO', 2),
('GUIA009', '2024-10-17 14:55:00', 'Bufanda Burberry + Abrigo', 'Cliente I', 'Villavicencio', 'Carrera 42 #29-15', 'ENTREGADO', 3),
('GUIA010', '2024-10-17 18:35:00', 'Converse + Zapatillas Puma', 'Cliente J', 'Ibagué', 'Calle 10 #35-90', 'ENTREGADO', 4),
('GUIA011', '2024-10-18 12:20:00', 'Sandalias Crocs + Pantalón', 'Cliente K', 'Montería', 'Av 1 #50-25', 'PENDIENTE', 5),
('GUIA012', '2024-10-18 16:10:00', 'Guantes UA + Jeans', 'Cliente L', 'Valledupar', 'Carrera 14 #22-60', 'EN_TRANSITO', 6);

-- 40 Ventas Detalle (distribuidos en ventas 1-12, totals aproximados coinciden)
INSERT INTO ventas_detalle (venta_id, producto_id, talla, cantidad, precio_unit) VALUES
(1,1,'M',2,29.99),
(1,3,'42',2,39.99),
(2,2,'L',1,49.99),
(2,4,'S',1,39.99),
(3,8,'M',1,199.99),
(3,20,'L',1,19.99),
(4,5,'XL',1,39.99),
(4,9,'42-44',2,9.99),
(5,7,'41',1,129.99),
(5,15,'Uni',1,59.99),
(5,6,'32',1,59.99),
(6,16,'Uni',1,79.99),
(7,11,'L',2,34.99),
(7,12,'M',1,29.99),
(8,10,'M',1,24.99),
(8,17,'XL',1,25.99),
(9,19,'Uni',1,149.99),
(9,14,'S',1,89.99),
(9,1,'M',1,29.99),
(10,18,'39',1,64.99),
(10,3,'42',1,79.99),
(11,13,'40',1,44.99),
(11,2,'L',1,49.99),
(11,4,'S',1,59.99),
(12,20,'L',2,19.99),
(12,9,'42-44',3,9.99),
(12,5,'XL',1,39.99),
(1,9,'42-44',1,9.99),
(2,10,'M',1,24.99),
(3,12,'M',1,29.99),
(4,16,'Uni',1,79.99),
(5,8,'M',1,199.99),
(6,15,'Uni',1,59.99),
(7,6,'32',1,69.99),
(8,13,'40',1,44.99),
(9,17,'XL',1,25.99),
(10,11,'L',1,34.99),
(11,14,'S',1,89.99),
(12,19,'Uni',1,149.99),
(1,20,'L',1,19.99),
(2,7,'41',1,129.99);

-- MIGRACIÓN FK USUARIOS: Permitir DELETE con SET NULL (ejecutar UNA VEZ)
ALTER TABLE ventas MODIFY COLUMN vendedor_id INT NULL;
ALTER TABLE ventas DROP FOREIGN KEY ventas_ibfk_1;
ALTER TABLE ventas ADD CONSTRAINT fk_ventas_vendedor 
  FOREIGN KEY (vendedor_id) REFERENCES usuarios(id) ON DELETE SET NULL;

ALTER TABLE envios MODIFY COLUMN vendedor_id INT NULL;
ALTER TABLE envios DROP FOREIGN KEY envios_ibfk_1;
ALTER TABLE envios ADD CONSTRAINT fk_envios_vendedor 
  FOREIGN KEY (vendedor_id) REFERENCES usuarios(id) ON DELETE SET NULL;

-- MIGRACION para DBs existentes (ejecutar UNA VEZ después del primer cambio)
-- ALTER TABLE ventas_detalle MODIFY COLUMN producto_id INT NULL;
-- ALTER TABLE ventas_detalle DROP FOREIGN KEY ventas_detalle_ibfk_2; 
-- ALTER TABLE ventas_detalle ADD CONSTRAINT fk_ventas_detalle_producto 
--   FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL;

