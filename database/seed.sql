-- ============================================================
-- Seed Script: datos demo para "Finanzas Personales"
-- Las inserciones son NO duplicadas: verifican existencia previa.
-- Sólo se inserta si la tabla correspondiente está vacía o el registro
-- no existe todavía.
-- ============================================================

-- --- Usuarios demo --------------------------------------------------------
-- Contraseña de ambos usuarios: "demo1234" (hash bcrypt generado).
-- Si ya existe algún usuario, no se duplica.
INSERT INTO usuarios (nombre, email, contrasena_hash)
SELECT 'Usuario Demo', 'demo@finanzas.com',
       '$2b$12$JWs1JiLhDSujq0lBBuvrQO4PVyXG8V0OyyCqE0S0W0jY3e0uR8pKW'
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'demo@finanzas.com'
);

-- --- Categorías -----------------------------------------------------------
-- Insertamos categorías de gasto e ingreso solo si no existen (por nombre+tipo).
INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Alimentación', 'gasto', 'Compras de supermercado y comida', '#EF4444'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Alimentación' AND tipo = 'gasto');

INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Transporte', 'gasto', 'Gasolina, transporte público, taxis', '#F59E0B'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Transporte' AND tipo = 'gasto');

INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Vivienda', 'gasto', 'Renta, servicios e hipoteca', '#8B5CF6'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Vivienda' AND tipo = 'gasto');

INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Entretenimiento', 'gasto', 'Cine, streaming, salidas', '#06B6D4'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Entretenimiento' AND tipo = 'gasto');

INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Salud', 'gasto', 'Consultas, medicinas y seguros', '#10B981'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Salud' AND tipo = 'gasto');

INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Educación', 'gasto', 'Cursos, libros y colegiaturas', '#3B82F6'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Educación' AND tipo = 'gasto');

INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Sueldo', 'ingreso', 'Ingresos por trabajo', '#22C55E'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Sueldo' AND tipo = 'ingreso');

INSERT INTO categorias (nombre, tipo, descripcion, color)
SELECT 'Freelance', 'ingreso', 'Trabajos independientes', '#14B8A6'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nombre = 'Freelance' AND tipo = 'ingreso');

-- --- Movimientos demo -----------------------------------------------------
-- Solo se insertan si la tabla está vacía (para no duplicar en re-ejecuciones).
INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'ingreso', 3000.00, '2026-01-05', 'Salario mensual'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Sueldo' AND c.tipo = 'ingreso'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 320.00, '2026-01-03', 'Supermercado quincenal'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Alimentación' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 150.00, '2026-01-10', 'Combustible'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Transporte' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 800.00, '2026-01-01', 'Renta mensual'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Vivienda' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 90.00, '2026-02-02', 'Supermercado'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Alimentación' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 650.00, '2026-02-07', 'Renta'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Vivienda' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 220.00, '2026-02-14', 'Salida y cine'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Entretenimiento' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'ingreso', 500.00, '2026-02-15', 'Proyecto freelance'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Freelance' AND c.tipo = 'ingreso'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 300.00, '2026-03-01', 'Supermercado'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Alimentación' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 810.00, '2026-03-05', 'Renta'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Vivienda' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 1200.00, '2026-03-12', 'Gasto médico inesperado'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Salud' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 340.00, '2026-03-18', 'Compras del mes'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Alimentación' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);

INSERT INTO ingresos_gastos (usuario_id, categoria_id, tipo, monto, fecha, descripcion)
SELECT u.id, c.id, 'gasto', 140.00, '2026-03-22', 'Combustible'
FROM usuarios u
JOIN categorias c ON c.nombre = 'Transporte' AND c.tipo = 'gasto'
WHERE u.email = 'demo@finanzas.com'
  AND NOT EXISTS (SELECT 1 FROM ingresos_gastos);
