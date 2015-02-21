Proyecto final de la asignatura de Inteligencia Artificial de 3º de Grado en Ingenieria Informatica - Ingenieria de Software de la universidad de Sevilla.
#Inversion de SLD resolucion con Python
##1. Introduccion<br>
Desde el punto de vista clasico, el Aprendizaje Automatico es el area de la Inteligencia
Articial cuyo objetivo es la sntesis de nuevos conocimientos a partir de la experiencia.
Durante las decadas de los setenta y ochenta el estudio de este problema dio lugar a
distintos sistemas computacionales como el caso del ID3 [5]. No obstante, a pesar del exito
obtenido sobre problemas reales, estos sistemas presentaban dos problemas importantes:
De un lado, una representacion formal limitada, equivalente al de la logica proposicional.
De otro lado, dicultad en el manejo del conocimiento base.
A nales de los a~nos ochenta, Stephen Muggleton y Wray Buntine [3] tuvieron la idea de
aplicar la logica clausal con variables y las tecnicas de la Programacion Logica al problema
del Aprendizaje, naciendo de este modo la Programacion Logica Inductiva 1
La Programacion Logica Inductiva (PLI) [2] puede denirse con el area de la Inteligencia
Articial donde con
uyen el Aprendizaje Automatico y la Programacion Logica y
su principal objetivo es el desarrollo de teoras y algoritmos para el aprendizaje inductivo
de programas logicos. La PLI toma toma del aprendizaje automatico sus objetivos, esto
es, la sntesis de nuevos conocimientos a partir de la experiencia. La Programacion Logica
aporta su representacion del conocimiento con formulas de la logica clausal, su orientacion
semantica y sus tecnicas.
De manera informal, podemos plantear el problema que intenta resolver la PLI del siguiente
modo: Dado un conocimiento base T y un conjunto de entrenamiento E, encontrar
una hipotesis H que junto con T explique E.
##2. Objetivo <br>
A lo largo de los a~nos se han desarrollado muy diversas tecnicas y algoritmos de
aprendizaje en el marco de la PLI. En el presente trabajo se pide que el alumno profundice
en el estudio y comprension de algunos de los operadores que llevan a cabo la inversion
de la resolucion SLD.<br>
![/images/1.png](/images/1.png)<br>
####2.1. V-operadores
La Figura 1 muestra esquematicamente un paso de resolucion. La resolucion deriva la
clausula C en el vertice de la V a partir de las clausulas C1 y C2 de los brazos 2. Podemos
representar la resolucion como la siguiente regla de inferencia<br>
<br><br>
![/images/2.png](/images/2.png)<br><br>
Como caso particular, podramos considerar<br>
**Ejemplo 1:**
<br><br>
![/images/3.png](/images/3.png)<br><br>
Usando resolucion, obtenemos C a partir de C1 y C2. Un nuevo ejemplo, usando
smbolos de funcion, pero donde no consideramos S y T es el siguiente<br>
**Ejemplo 2:**
<br><br>
![/images/4.png](/images/4.png)<br><br>
Los V -operadores son operadores que invierten el proceso de resolucion, de manera
que derivan la clausula de uno de los brazos a partir de la clausula del otro brazo y la del
vertice. Se denomina operador absorcion al operador que permite construir C2 a partir de
C y C1<br>
<br><br>
![/images/5.png](/images/5.png)<br><br>
![/images/6.png](/images/6.png)<br><br>
Se llama operador identicacion al operador que nos permite construir C1 dados C y C2<br>
<br><br>
![/images/7.png](/images/7.png)<br><br>
###2.2. W-operadores
Ademas de los V-operadores, existen otras reglas para la inversion de la resolucion:
la intra-construccion y la inter-construccion. Ambas reglas se conocen con el nombre
conjunto de W-operadores (Figura 2).<br>
<br><br>
![/images/8.png](/images/8.png)<br><br>
Notese que mediante la aplicacion de los W-operadores debemos considerar un nuevo
literal que no aparece en la entrada del operador.<br>
**Ejemplo 3 (para Intra-construccion):**
<br><br>
![/images/9.png](/images/9.png)<br><br>
**Ejemplo 4 (para Inter-construccion):**
<br><br>
![/images/10.png](/images/10.png)<br><br>
En los W operadores, partimos de dos clausulas B1 y B2 y a partir de ellas buscamos
las clasulas C1, C2 y C de manera que B1 se obtenga a partir de C1 y C mediante resolucion
y B2 se obtenga por resolucion a partir de C y C2.<br>

###2.3. Objetivo especco del trabajo<br>
Implementacion de los cuatro operadores (Absorcion, Identificacion, Inter-
construccion e Intra-construccion) en logica clausal con smbolos de funcion. El
programa debe especicar las clasusulas obtenidas para cada operador y las unicaciones
necesarias. La implementacion deberealizarse en el lenguaje de programacion Python 3.2
o Python 3.3. El sistema de representacion se deja a la eleccion del alumno, pero debe ser
sucientemente general para poder representar cualquier clausula denida. En la web se
pueden encontrar diversas variantes del algoritmo. El trabajo debe incluir detalladamente
que variante del algoritmo se ha implementado.
