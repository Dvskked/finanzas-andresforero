-- Datos de prueba iniciales (SEED)
-- Usuario de prueba: correo ana@example.com / contraseña: finanzas123

INSERT INTO usuarios (nombre, correo, contrasena_hash)
VALUES ('Ana Torres', 'ana@example.com', '$2b$12$vM8qpmlNNv8HHNxRGUWm3ulI91RbDdTKyMmtzCErSkiEV8QgXeB/a');

-- La serie auto increment de usuarios ya empezó en 1, así que hacemos
-- referencia directa al id_usuario = 1.

INSERT INTO categorias (nombre, tipo, id_usuario) VALUES
('Salario', 'ingreso', 1),
('Freelance', 'ingreso', 1),
('Alimentación', 'gasto', 1),
('Transporte', 'gasto', 1),
('Entretenimiento', 'gasto', 1),
('Salud', 'gasto', 1);

INSERT INTO ingresos_gastos (id_usuario, id_categoria, tipo, monto, fecha, descripcion) VALUES
(1, 1, 'ingreso', 2500000.00, '2026-06-01', 'Pago mensual'),
(1, 1, 'ingreso', 2500000.00, '2026-07-01', 'Pago mensual'),
(1, 3, 'gasto', 320000.00, '2026-06-05', 'Mercado del mes'),
(1, 3, 'gasto', 300000.00, '2026-07-04', 'Mercado del mes'),
(1, 4, 'gasto', 90000.00, '2026-06-07', 'Transporte semanal'),
(1, 4, 'gasto', 95000.00, '2026-07-07', 'Transporte semanal'),
(1, 5, 'gasto', 150000.00, '2026-06-10', 'Cine y salidas'),
(1, 5, 'gasto', 140000.00, '2026-07-10', 'Cine y salidas'),
(1, 6, 'gasto', 800000.00, '2026-07-15', 'Consulta médica de urgencia');
