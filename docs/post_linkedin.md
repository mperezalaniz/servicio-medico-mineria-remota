En una mina de Santa Cruz, el hospital más cercano queda a dos o tres horas por ruta. Esa distancia no se puede cambiar. Lo que pasa entre el aviso y la salida de la ambulancia, sí.

Trabajé cinco años en salud ocupacional en minería en Santa Cruz y quise medir cuánto pesa cada tramo de una emergencia grave. Armé un modelo Monte Carlo en Python con 20.000 casos por escenario. Usé rutas reales de OpenStreetMap hasta los hospitales de Perito Moreno, Las Heras, Caleta Olivia y Comodoro Rivadavia, y los tiempos dentro del sitio como supuestos explícitos.

Esto es lo que salió:

El 49% del tiempo hasta el hospital más cercano pasa dentro del sitio.

La espera más larga es coordinar la derivación: 41 minutos de mediana, y arranca recién cuando termina la estabilización.

Con dos cambios de proceso, la ambulancia sale 60 minutos antes en el caso típico y 75 minutos antes en los más difíciles. El primero es un protocolo de derivación acordado de antemano, coordinado mientras se estabiliza al paciente. El segundo, brigadistas en cada frente bajo mina. Sin comprar un solo equipo.

Con esos brigadistas, el primer contacto con el paciente baja de 23 a 12 minutos de mediana.

Los casos que llegan a un hospital de alta complejidad en menos de 6 horas pasan de 17% a 83%.

Con esos números armé un plan de 100 días para liderar un servicio médico en sitio, con acta, cronograma, RACI, riesgos, indicadores y dos proyectos DMAIC. También un tablero semanal del servicio: carta de control de consultas, exámenes al día, brigadistas vigentes y stock crítico con kanban.

Los tiempos internos son supuestos y el tablero usa datos inventados, así que no hay información de ninguna empresa. Con registros reales de simulacros, el modelo se recalibra en una semana.

Simulador interactivo: mperezalaniz.github.io/servicio-medico-mineria-remota
Código, datos y plan de 100 días: github.com/mperezalaniz/servicio-medico-mineria-remota

Si trabajás en un servicio médico de minería u oil & gas, ¿qué tramo te cuesta más acortar?

#SaludOcupacional #Mineria #LeanSixSigma #ProjectManagement #DataAnalytics #Python #Enfermeria #RespuestaAEmergencias
