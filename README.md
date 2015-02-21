Proyecto final de la asignatura de Inteligencia Artificial de 3º de Grado en Ingenieria Informatica - Ingenieria de Software de la universidad de Sevilla.
#Inversion de SLD resolucion con Python
El siguiente texto esta copiado del pdf de definición del proyecto:
##1. Introduccion<br>
Desde el punto de vista clásico, el Aprendizaje Automatico es el área de la Inteligencia
Artificial cuyo objetivo es la síntesis de nuevos conocimientos a partir de la experiencia.
Durante las décadas de los setenta y ochenta el estudio de este problema dio lugar a
distintos sistemas computacionales como el caso del ID3. No obstante, a pesar del éxito
obtenido sobre problemas reales, estos sistemas presentaban dos problemas importantes:
* De un lado, una representación formal limitada, equivalente al de la logica proposicional.
* De otro lado, dificultad en el manejo del conocimiento base.
A finales de los añnos ochenta, Stephen Muggleton y Wray Buntine tuvieron la idea de
aplicar la logica clausal con variables y las tecnicas de la Programacion Logica al problema
del Aprendizaje, naciendo de este modo la Programacion Logica Inductiva
La Programación Lógica Inductiva (PLI) puede definirse con el área de la Inteligencia
Artificial donde conuyen el Aprendizaje Automatico y la Programación Lógica y
su principal objetivo es el desarrollo de teorías y algoritmos para el aprendizaje inductivo
de programas lógicos. La PLI toma toma del aprendizaje automático sus objetivos, esto
es, la síntesis de nuevos conocimientos a partir de la experiencia. La Programación Lógica
aporta su representación del conocimiento con fórmulas de la lógica clausal, su orientación
semántica y sus técnicas.
De manera informal, podemos plantear el problema que intenta resolver la PLI del siguiente
modo: Dado un conocimiento base T y un conjunto de entrenamiento E, encontrar
una hipótesis H que junto con T explique E.
##2. Objetivo <br>
A lo largo de los años se han desarrollado muy diversas técnicas y algoritmos de
aprendizaje en el marco de la PLI. En el presente trabajo se pide que el alumno profundice
en el estudio y comprensión de algunos de los operadores que llevan a cabo la inversión
de la resolución SLD.<br>
![/images/1.png](/images/1.png)<br>
####2.1. V-operadores
La Figura 1 muestra esquemáticamente un paso de resolución. La resolución deriva la
clausula C en el vértice de la V a partir de las cláusulas C1 y C2 de los brazos 2. Podemos
representar la resolución como la siguiente regla de inferencia<br>
<br><br>
![/images/2.png](/images/2.png)<br><br>
Como caso particular, podríamos considerar<br>
**Ejemplo 1:**
<br><br>
![/images/3.png](/images/3.png)<br><br>
Usando resolución, obtenemos C a partir de C1 y C2. Un nuevo ejemplo, usando
símbolos de función, pero donde no consideramos S y T es el siguiente<br>
**Ejemplo 2:**
<br><br>
![/images/4.png](/images/4.png)<br><br>
Los V -operadores son operadores que invierten el proceso de resolución, de manera
que derivan la cláusula de uno de los brazos a partir de la cláusula del otro brazo y la del
vértice. Se denomina operador absorcion al operador que permite construir C2 a partir de
C y C1<br>
<br><br>
![/images/5.png](/images/5.png)<br><br>
![/images/6.png](/images/6.png)<br><br>
Se llama operador identificación al operador que nos permite construir C1 dados C y C2<br>
<br><br>
![/images/7.png](/images/7.png)<br><br>
###2.2. W-operadores
Además de los V-operadores, existen otras reglas para la inversión de la resolución:
la intra-construcción y la inter-construcción. Ambas reglas se conocen con el nombre
conjunto de W-operadores (Figura 2).<br>
<br><br>
![/images/8.png](/images/8.png)<br><br>
Nótese que mediante la aplicación de los W-operadores debemos considerar un nuevo
literal que no aparece en la entrada del operador.<br>
**Ejemplo 3 (para Intra-construccion):**
<br><br>
![/images/9.png](/images/9.png)<br><br>
**Ejemplo 4 (para Inter-construccion):**
<br><br>
![/images/10.png](/images/10.png)<br><br>
En los W operadores, partimos de dos cláusulas B1 y B2 y a partir de ellas buscamos
las clasulas C1, C2 y C de manera que B1 se obtenga a partir de C1 y C mediante resolucion
y B2 se obtenga por resolución a partir de C y C2.<br>

###2.3. Objetivo especco del trabajo<br>
Implementación de los cuatro operadores (Absorción, Identificación, Inter-
construcción e Intra-construcción) en lógica clausal con símbolos de función. El
programa debe especificar las clásusulas obtenidas para cada operador y las unificaciones
necesarias. La implementación deberealizarse en el lenguaje de programación Python 3.2
o Python 3.3. El sistema de representación se deja a la elección del alumno, pero debe ser
suficientemente general para poder representar cualquier cláusula definida. En la web se
pueden encontrar diversas variantes del algoritmo. El trabajo debe incluir detalladamente
qué variante del algoritmo se ha implementado.
