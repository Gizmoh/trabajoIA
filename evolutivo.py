# -*- coding: utf-8 -*-

import random
import sys
import numpy as np
import csv
from py4j.java_gateway import JavaGateway
from config import DOORS, \
                    SOLUTIONS, \
                    NETLOGOMODEL, \
                    PLANFILE, \
                    PLANARRAY, \
                    doorsFile, \
                    createPlanFile

class Posicion():

    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def obtenerVecinos(self, posiciones):
        # A partir de un punto dado, determina cuales son los vecinos.
        vecinos = []
        for p in posiciones:
            if self.x + 1 == p.x and self.y == p.y:
                vecinos.append(p)
            if self.x - 1 == p.x and self.y == p.y:
                vecinos.append(p)
            if self.y - 1 == p.y and self.x == p.x:
                vecinos.append(p)
            if self.y + 1 == p.y and self.x == p.x:
                vecinos.append(p)
        return vecinos


class Individuo():

    def __init__(self, genes):
        self.fitness = 0
        self.genes = []
        self.fitnessList = []
        self.suman = 0
        # almacenamos los genes en una lista simple de numeros
        for g in range(0, 10):
            self.genes.append(genes[g])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def evaluar(self, bridge):
        # Esta funcion es la que deberia calcular el fitness del individuo
        # donde el fitness esta dado por el valor de ticks de la simulacion

        generarDoors(self.genes)
        fitnessList = []
        # Con esta funcion se realizan 30 pruebas distintas por individuo, se almacenan
        # los resultados y se obtiene un promedio que corresponde a la evaluacion del individuo
        for i in range(0,10):
            bridge.command("load-fixed-plan-file")
            bridge.command("load-fixed-door-file")
            bridge.command("generate-population")
            bridge.command("repeat 250 [ go ]")
            new_fitness = bridge.report("ticks")
            self.fitnessList.append(new_fitness)
        self.suman = 0
        for x in self.fitnessList:
            self.suman = self.suman + x
        self.fitness = self.suman/len(self.fitnessList)
        #bridge.command("repeat 200 [ go ]")
        #new_fitness = bridge.report("ticks")
        #if (self.fitness == 0):
        #    
        #    self.fitness = new_fitness

        #elif(self.fitness > new_fitness):

        #    self.fitness = new_fitness
        #else:
        #    self.fitness = self.fitness


def obtenerPosiciones(file):
    posiciones = []
    with open(file, 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.split(' ')
            m = Posicion(int(line[0]), int(line[1]), int(line[2]))
            posiciones.append(m)
    return posiciones


def obtenerGenes(posiciones):
    genes = []
    for punto in posiciones:
        if punto.tipo == 64:
            if validarPunto(punto, posiciones):
                genes.append(punto)
    return genes


def generarArchivo(genes):
    doors = open(DOORS, "w")
    for x in range(0, 5):
        punto = genes[random.randrange(0, len(genes))]
        doors.write("{0} {1} \n".format(punto.x, punto.y))
    doors.close()
    print "Generado puertas"

    sol = open(SOLUTIONS, "w")
    for x in range(0, len(genes)):
        punto = genes[x]
        sol.write("{0} {1} \n".format(punto.x, punto.y))
    sol.close()
    print "Generado soluciones"


def validarPunto(punto, posiciones):
    # retorna si un punto es valido como como posible puerta
    vecinos = punto.obtenerVecinos(posiciones)

    if len(vecinos) < 4:
        # descartamos los puntos que estan en los bordes
        return False
    else:
        # Muro izquierdo
        if vecinos[1].tipo == 2 and vecinos[2].tipo == 0:
            return True
        # Muros inferiores
        elif vecinos[3].tipo == 2 and vecinos[0].tipo == 0:
            return True
        # Muros superiores
        elif vecinos[0].tipo == 2 and vecinos[3].tipo == 0:
            return True
        # Muros derechos
        elif vecinos[1].tipo == 0 and vecinos[2].tipo == 2:
            return True
        # Cualquier otro caso.
        else:
            return False


def generarPoblacion(genes, poblacion):
    # retorna una lista de Individuos
    individuos = []
    for x in range(0, poblacion):
        genes_individuo = asignarGenes(genes)
        individuo = Individuo(genes_individuo)
        individuos.append(individuo)
    return individuos



def asignarGenes(genes):
    # retorna los genes del individuo, y verifica que los genes no se repitan.
    rango = len(genes)
    genes_individuo = []
    n_genes = 0

    lista_genes = []
    lista_genes.append(genes[random.randrange(0, rango)])
    for x in range(0, 4):
        continua = True
        while continua:
            gen = genes[random.randrange(0, rango)]
            if gen in lista_genes:
                continua = True
            else:
                lista_genes.append(gen)
                continua = False
    for x in range(0, len(lista_genes)):
        genes_individuo.append(lista_genes[x].x)
        genes_individuo.append(lista_genes[x].y)
    return genes_individuo


def ordenarIndividuos(individuos):
    # Ordenamos los individuos y luego asignamos la categoria
    # Para luego seleccionarlos en la ruleta.
    individuos = sorted(
        individuos, key=lambda individuo: individuo.fitness, reverse=False)
    return individuos


#def seleccionarIndividuos(individuos):
    # Aca hay que seleccionar el metodo de seleccion de los individuos
    # Seleccionar los n mejores individuos que pasaran al crossover.
    #individuos = ordenarIndividuos(individuos)
    #seleccionados = []
    # Seleccionamos siempre al mejor de cada generacion
    #seleccionados.append(individuos[0])

    #weights = [0.5, 0.25, 0.15, 0.1]

    #se seleccionan aleatoriamente 30 individuos de forma uniforme
    #for x in range(1, 30):
    #    sigue = True
    #    while sigue:
    #        choices = [random.randrange(1, 50), random.randrange(
    #            51, 75), random.randrange(76, 90), random.randrange(90, 100)]
    #        rnd = np.random.choice(choices, p=weights)
    #        seleccionado = individuos[rnd]
    #        if seleccionado in seleccionados:
    #            sigue = True
    #        else:
    #            seleccionados.append(individuos[rnd])
    #            sigue = False
    #seleccionados = ordenarIndividuos(seleccionados)
    #return seleccionados


#def cruzar(padre, madre):
#    # Cruzamos dos individuos se cruzan individuos en los que no se repiten sus genes al
#    #hacer el cruce

#    continua = True
#    
#    pos = random.randrange(0, 5)  # randrange (0, n-1)
#    if pos == 0:
#        pos = 2
#    else:
#        pos = 2 * pos

#    genes_hijo1 = []
#    for x in range(0, pos):
#        genes_hijo1.append(padre.genes[x])

#    for x in range(pos, 10):
#        genes_hijo1.append(madre.genes[x])

#    genes_hijo2 = []
#    for x in range(0, pos):
#        genes_hijo2.append(madre.genes[x])
#
#    for x in range(pos, 10):
#        genes_hijo2.append(padre.genes[x])
#    #buscando duplicados
#    duplicados1 = False
#    duplicados2 = False

#    for i in range(0,5):
#        for j in range(0,5):
#            if i != j:
#                if [genes_hijo1[(i*2)],genes_hijo1[(i*2)+1]] == [genes_hijo1[(j*2)],genes_hijo1[(j*2)+1]]:
#                    duplicados1 = True
#                if [genes_hijo2[(i*2)],genes_hijo2[(i*2)+1]] == [genes_hijo2[(j*2)],genes_hijo2[(j*2)+1]]:
#                    duplicados2 = True
#    hijos = []
#    if not duplicados1 and not duplicados2:
#        hijo1 = Individuo(genes_hijo1)
#        hijos.append(hijo1)
#        hijo2 = Individuo(genes_hijo2)
#        hijos.append(hijo2)
#    return hijos


#def reproducirIndividuos(individuos, bridge):
    # Hay un 75% de probabilidades que un individuo no se reproduzca
#    nueva_poblacion = individuos
#    choices = ["RP", "NP"]
#    weights = [0.40, 0.60]
#    n_individuos = len(nueva_poblacion)
#
#    while n_individuos < 99:
#
#        rnd = np.random.choice(choices, p=weights)
#        # tomamos un padre y madre aleatorio
#        padre = individuos[random.randrange(0, len(individuos) - 1)]
#        madre = individuos[random.randrange(0, len(individuos) - 1)]
#
#        if rnd == "RP":
#            hijos = cruzar(padre, madre)
#            if hijos != []:
#                hijos[0].evaluar(bridge)
#                hijos[1].evaluar(bridge)
#                nueva_poblacion.append(hijos[0])
#                nueva_poblacion.append(hijos[1])
#                n_individuos = n_individuos + 2
#        else:
#            pass
#
#    nueva_poblacion = ordenarIndividuos(nueva_poblacion)
#    return nueva_poblacion

def cruzeIndividuos(individuos, posiciones, bridge):
    testX = [0,2,4,6,8]
    testY = [1,3,5,7,9]
    alpha = individuos[0]
    for beta in range(1,len(individuos)):
        for q in testX:
            for w in testX:
                if alpha.genes[q]==individuos[beta].genes[w]:
                    temp = (individuos[beta].genes[w+1]+ alpha.genes[q+1])/2
                    for x in posiciones:
                        if alpha.genes[q]==x.x and int(round(temp)) == x.y:
                            asdufee = x
                            if asdufee.tipo ==64:
                                #print "individuo beta ", individuos[beta].genes[w] , individuos[beta].genes[w+1] ,"individuo alpha ", alpha.genes[q] , alpha.genes[q+1]
                                individuos[beta].genes[w+1] = int(round(temp))
                                #print "individuo beta ", individuos[beta].genes[w] , individuos[beta].genes[w+1] ,"individuo alpha ", alpha.genes[q] , alpha.genes[q+1]
        for q in testY:
            for w in testY:
                if alpha.genes[q]==individuos[beta].genes[w]:
                    temp = (individuos[beta].genes[w-1]+ alpha.genes[q-1])/2
                    for x in posiciones:
                        if alpha.genes[q]==x.x and int(round(temp)) == x.y:
                            asdufee = x
                            if asdufee.tipo ==64:
                                #print "individuo beta ", individuos[beta].genes[w] , individuos[beta].genes[w-1] ,"individuo alpha ", alpha.genes[q] , alpha.genes[q-1]
                                individuos[beta].genes[w-1] = int(round(temp))
                                #print "individuo beta ", individuos[beta].genes[w] , individuos[beta].genes[w-1] ,"individuo alpha ", alpha.genes[q] , alpha.genes[q-1]

def descarteIndividuos (individuos, porcentaje, genes):
    listaSize = len(individuos)
    descarte = int(round(listaSize*30/100))
    individuos = individuos[:-descarte or NONE]
    print len(individuos)
    for x in range(0,descarte):
        genes_individuo = asignarGenes(genes)
        individuo = Individuo(genes_individuo)
        individuos.append(individuo)
    print len(individuos)


#def mutarIndividuos(individuos, genes, bridge):
    # Mutar con probabilidad de 0.01 algun gen de un individuo
    #choices = ["M", "N"]
    #weights = [0.01, 0.99]
    #mutados = []
    #for i in individuos:
    #    for pos in [0,1,2,3,4]:
    #        rnd = np.random.choice(choices, p=weights)
    #        if rnd == "M":
    #            #pos = random.randrange(0, 5)  # randrange (0, n-1)
    #            continua = True
    #            while continua:
    #                iguales = 0
    #                gen = genes[random.randrange(0, len(genes))]
    #                for x in range(0, 5):
    #                    if gen.x != i.genes[2 * x] and gen.y != i.genes[(2 * x) + 1]:
    #                        iguales = iguales
    #                    else:
    #                       iguales = iguales + 1

    #                if iguales == 0:
    #                    continua = False
    #                    i.genes[2 * pos] = gen.x
    #                    i.genes[2 * pos + 1] = gen.y
    #                else:
    #                    continua = True  
    #            #Se cambia fitness para la nueva evaluacion
    #            i.fitness = 0
    #            i.evaluar(bridge)
    #        else:
    #            pass
    #    mutados.append(i)

    #mutados = ordenarIndividuos(mutados)
    #return mutados

def Xmen (individuos, posiciones, mutacion):
    testX = [0,2,4,6,8]
    testY = [1,3,5,7,9]
    opcion = ["X","Y"]
    for x in range(0,mutacion):
        elige = random.choice(opcion)
        if elige=="X":
            W = random.randint(0,len(individuos)-1)
            temp = individuos[W]
            Q = random.choice(testX)
            newX = temp.genes[Q] + random.randint(-2,2)
            for x in posiciones:
                if newX == x.x and temp.genes[Q+1] == x.y:
                    asdufee = x
                    if asdufee.tipo ==64:
                        individuos[W].genes[Q] = newX
        if elige=="Y":
            W = random.randint(0,len(individuos)-1)
            temp = individuos[W]
            Q = random.choice(testY)
            newY = temp.genes[Q] + random.randint(-2,2)
            for x in posiciones:
                if temp.genes[Q-1] == x.x and newY == x.y:
                    asdufee = x
                    if asdufee.tipo ==64:
                        individuos[W].genes[Q] = newY
        





def generarDoors(genes, file=None):
    # modificado por qe ahora debe funcionar con una lista simple
    if file == None:
        doors = open(DOORS, "w")
    else:
        doors = open(doorsFile(file), "w")
    for x in range(0, 10):
        doors.write("{0} ".format(genes[x]))
        if x in [1, 3, 5, 7, 9]:
            doors.write("\n")
    doors.close()


if __name__ == "__main__":
    try:
        numero_pruebas = int(sys.argv[1])
        plan_elegido = PLANARRAY[int(sys.argv[2])]
        porcentajeDescarte = int(sys.argv[3])
        mutacion = int(sys.argv[4])
        print u"Total de evaluaciones a realizar por plan: ", sys.argv[1]
        print u'El plan elegido es: ', plan_elegido
        print u'El porcentaje de descarte es: ', porcentajeDescarte
        print u'La cantidad de mutaciones es: ', mutacion
    except:
        numero_pruebas = 10
        plan_elegido = PLANARRAY[0]
        porcentajeDescarte = 30
        mutacion = 5
        print u"El número de pruebas a realizar será el por defecto (10 rondas)"
        print u'El plan elegido es: ', plan_elegido
        print u'El porcentaje de descarte es: ', porcentajeDescarte
        print u'La cantidad de mutaciones es: ', mutacion
    gw = JavaGateway()  # New gateway connection
    bridge = gw.entry_point  # The actual NetLogoBridge object
    bridge.openModel(NETLOGOMODEL)
    poblacion = 100
    Xfile = open('resultados.csv',"w")
    writer = csv.writer(Xfile,dialect='excel')
    writer.writerow(["Iteracion/Individuo"]+range(0,poblacion))

    createPlanFile(plan_elegido)
    posiciones = obtenerPosiciones(PLANFILE)
    # en genes se guardan todas las posibles puertas
    genes = obtenerGenes(posiciones)
    # generarArchivo(genes)

    individuos = generarPoblacion(genes,poblacion)

    # aca especificamos el numero de generaciones
    for x in range(0, numero_pruebas):
        print "generacion: {0}".format(x)
        for individuo in individuos:
            # Ahora se supone que hay que evaluar cada uno de los
            # individuos para determinar el fitness de cada uno
            individuo.evaluar(bridge)

        individuos = ordenarIndividuos(individuos)
        superFitness = [x]
        for x in individuos:
            superFitness.append(x.fitness)
        writer.writerow(superFitness)
        cruzeIndividuos(individuos,posiciones,bridge)
        mejor = individuos[0]
        print "mejor     : {0}".format(mejor.fitness)
        descarteIndividuos(individuos,porcentajeDescarte,genes)
        Xmen(individuos,posiciones,mutacion)

        #individuos = reproducirIndividuos(individuos,bridge)

        #individuos = mutarIndividuos(individuos, genes, bridge)
    Xfile.close()
    generarDoors(mejor.genes, plan_elegido)