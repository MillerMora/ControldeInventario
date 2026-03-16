-- Esquema de base de datos MySQL para Almacor

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
  password_hash VARBINARY(255) NOT NULL,
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

-- Detalle de ventas
CREATE TABLE IF NOT EXISTS ventas_detalle (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venta_id INT NOT NULL,
  producto_id INT NOT NULL,
  talla VARCHAR(30) NOT NULL,
  cantidad INT NOT NULL,
  precio_unit DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
  FOREIGN KEY (producto_id) REFERENCES productos(id)
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

-- Usuario admin por defecto (password: admin)
-- El hash debe generarse con bcrypt desde la aplicación.

