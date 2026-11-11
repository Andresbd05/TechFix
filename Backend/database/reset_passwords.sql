-- Reinicia las contrasenas de los usuarios de TechFix a una clave conocida.
-- Ejecutar DESPUES de haber cargado techfix_db.sql.
-- Las contrasenas se guardan cifradas (scrypt, de una sola via): esto NO
-- recupera las viejas, las reemplaza por claves nuevas que luego puedes cambiar.

USE techfix_db;

UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$azAn7BdbBHaDE58Y$1c2bac505780b6c1da7fbf3c5c6037cda55e319ae531764c74c572d7d2171807da55fe5c59a3b8daa35b54ae834217022170bf337843553fc6ba7c0ab8544d2c' WHERE username = 'admin';
UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$ZoeGX6PUAH4x6y38$b0035d00e881564f18ca940a6149534b08e8eb686c235d4364c82bb353deb30eaaaa02abde2ff7a48234b5ee80139121445cd5fc2b755c1be42841c8193aa52b' WHERE username = 'propietario';
UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$JdhBqszWM2uukRGq$d91a64655578dabc1c9ab8c759792cef0053cbc417cfe389f51474de602377507bb5c0c4402bfafe3bbb5428847a63a97153bc3aa14c5540f07fe095d3c78c7b' WHERE username = 'invitado';
UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$J5vJcDOC13chmaic$a24630d058de89ad02609fde662b16a7e3b1c9b740982a4f168207fecd1537aad7c6906e56c56596d167a0e7f8f895838c3bafcb1d2700c7b3072df4daa8d59e' WHERE username = 'javier';
UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$tASeo433M88jydrZ$84d8d957fef8a279277d59bf2d4d7768e511e080a93edcba237c0339d481326a8bb3850020f1b56a79e959e2afd06a0e4b464470dd26d0e1689f9e72d468dbda' WHERE username = 'sofia';
UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$pCs5U1QnDftfY4qH$47667b65b6e2e0452fb2a764cb0115d4e8c6697f5d1592d2a4e290f72a1a7112f5be9b3b6be0b5cf66695329488d24cfd91295c92a6d96a70dcd32eb9b5a8a64' WHERE username = 'andres';
UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$mnAsvvrZTozUUsK1$43c97f7d19e910e3279d6406d4e251f4175f234c9ce05627865c838be7d1123ea84b0aa9eb528f5631ec25997b2cb5e12f9168c76c2ab715f10305ffeb5143ac' WHERE username = 'camilo';
UPDATE usuarios SET password_hash = 'scrypt:32768:8:1$68bhNP6lu8rpbOpR$0171a55b87a1241f3aa84112458ea5a769394ed5d5a2d23f25b8f60a5315c010a6c31a3e36c3bf10c3f3f16426667878f6048a812ae5d2f8e805514c9c6009c9' WHERE username = 'natalia';

-- Usuarios y claves que quedan (cambialas desde la app despues de entrar):
--   admin        / Admin123*    (admin)
--   propietario  / Dueno123*    (propietario)
--   invitado     / Invitado123* (invitado)
--   javier       / Tecnico123*  (tecnico)
--   sofia        / Tecnico123*  (tecnico)
--   andres       / Tecnico123*  (tecnico)
--   camilo       / Tecnico123*  (tecnico)
--   natalia      / Tecnico123*  (tecnico)
