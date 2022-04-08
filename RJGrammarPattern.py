#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 16:18:50 2020

@@author: A
@author: B


"""

from LayoutAtos import LayoutAtos 
from Util import Util
from Diario import Diario
from RioJaneiroDAO import RioJaneiroDAO
from Ato import Ato
from Comissoes import Comissoes
from Persistencia import Persistencia


t = u"u00b0"

import re

class RJGrammarPattern(LayoutAtos):    
   
    tipo = ""
    
    def do_diario(self, buffer, arquivo):
        print(arquivo)
        diario_pattern = re.compile('Ano\s([A-Z]*)\s•\sN\w\s([0-9]*)')        
        diario_edicao = diario_pattern.search(buffer)        
        print(diario_edicao.group(1))        
        print("Arquivo->"+arquivo+'\n')
        
        #Diário Suplementar
        diario_suplemento_pattern = re.compile('Diário Oficial do Município do Rio de Janeiro\s\|\s\w*\s\w*\s\|\s\w*\s\w*\s\|\s(Suplemento)')
        diario_suplemento = diario_suplemento_pattern.search(buffer)
        if diario_suplemento:
           tipo = 2 #Suplemento
        else:
           tipo = 1 #Normal 
        
        util = Util()
        diario = Diario()                
        RioDAO = RioJaneiroDAO()        
        diario.anoromano = (diario_edicao.group(1))
        diario.ano = (util.converteRomano(diario_edicao.group(1)))
        diario.numero = (diario_edicao.group(2))
        diario.nomearquivo = None 
        diario.datadiario = None 
        diario.tipo = (tipo)
        diario.identidade = None 
        diario.datagravacao = None #
        RioDAO.gravaDiario(diario)            
        
    def resolucoes(self, buffer, arquivo, arq1, criticas, contarq, data_e_hora, arqres, perc, train_data,  BL, BUFFER):
        print('ARQUIVO========================================================>',arquivo,'(CARGOS)', perc,'%')
        ################# PROCESSA CABEÇALHO DO DIARIO ################
        diario_pattern = re.compile('Ano\s([A-Z]*)\s•\sN\w\s([0-9]*)')        
        diario_edicao = diario_pattern.search(buffer)  
        print(buffer, file=BUFFER)
        
        diario_suplemento_pattern = re.compile('Diário Oficial do Município do Rio de Janeiro\s\|\s\w*\s\w*\s\|\s\w*\s\w*\s\|\s(Suplemento)')
        diario_suplemento = diario_suplemento_pattern.search(buffer)
        if diario_suplemento:
           tipo = 'SUPLEMENTAR' #Suplemento
        else:
           tipo = 'NORMAL' #Normal 
        util = Util()
        diario = Diario() 
        if (diario_edicao.group(1)):               
            diario.anoromano = '{: <6}'.format(((diario_edicao.group(1))))
            diario.ano = (util.converteRomano(diario_edicao.group(1)))
            diario.numero = '{:0>6}'.format((diario_edicao.group(2)))
            diario.tipo = '{: <12}'.format((tipo))
            if (diario.ano < 26):print("Diário anterior a 2013:", "Ano:", diario.ano, "Arquivo:", arquivo.upper(), file=criticas) 
        else:
            diario.anoromano = 'XXXXXX'
            diario.ano = 'XXXXXX'
            diario.numero = 'XXXXXX'
            diario.tipo = 'XXXXXXXXXXXX'

        print('', file=arq1)
        print('(<inst>-<loc>/<lab>)   ::PROCESSAMENTO DO DIÁRIO::', 'ANO:', diario.ano,'No.:', diario.numero, 'TIPO:', diario.tipo, '* RIO DE JANEIRO * ARQUIVO:',arquivo.upper(), 'SEQ.:', '{:0>4}'.format(contarq), '                                             ',data_e_hora,  file=arq1)
        print('', file=arq1) 
           
        #############################################################        
        resolucao_pattern = re.compile(r'^(\*RESOLUÇÕES|RESOLUÇÕES|RESOLUÇOES|RESOLUÇÃO|RESOLUÇAO|PORTARIAS|DECRETO RIO|PORTARIA)\s*(.)*\s*“P”.*',re.M)
        contador = 1
        cont=-1
        inicio = []
        bloco = []
        servidor = []
        tamanho = len(buffer)
        for resolucao in resolucao_pattern.finditer(buffer):
            inicio.append(resolucao.start())
            contador=contador + 1 
        inicio.append(tamanho)    
 
        for i in range(len(inicio)-1):
            bloco.append(inicio[i+1]-inicio[i])
            buffer_local = buffer[inicio[i]:inicio[i]+bloco[i]]
            print(buffer_local, file=BL)
            
            ###### Resolução #####
            resolucao1_pattern = re.compile(r'^(?P<resolucao1>\*RESOLUÇÕES|RESOLUÇÕES|RESOLUÇOES|RESOLUÇÃO|RESOLUÇAO|PORTARIAS|DECRETO RIO|PORTARIA)\s*(.)*\s*“P”(?P<detalhe_resolucao1>.*)',re.M)
            resolucao1 = resolucao1_pattern.search(buffer_local)
            if (resolucao1):
                Tipo = '{: <11}'.format(resolucao1.group('resolucao1'))
                Detalhe = resolucao1.group('detalhe_resolucao1')                
            else:
                #print('Não casou resolucao1')
                Tipo = 'SEM TIPO'
                Detalhe = 'SEM DETALHE'
            #####################
            
            #### Gestor #####
            gestor_pattern = re.compile(r'(?P<gestor>[O|A]*\s(SECRETÁRI[O|A]+|PROCURADOR[A]*|PREFEITO[A]*|COORDENADOR[A]*)[A-ZÁÚÍÃÓÇÊÉ\s-]+)')
            gestor = gestor_pattern.search(buffer_local)
            if (gestor):
                Gestor = gestor.group('gestor')
            else:
                Gestor = 'SEM GESTOR'
            ###### Fim Gestor
            
         ################################# RESOLUÇÕES COMPOSTAS #############################
            persistencia = Persistencia()
            if ((resolucao1.group('resolucao1') == '*RESOLUÇÕES') or (resolucao1.group('resolucao1') == 'RESOLUÇÕES') or (resolucao1.group('resolucao1') == 'RESOLUÇOES') or (resolucao1.group('resolucao1') == 'RESOLUCOES') or (resolucao1.group('resolucao1') == 'PORTARIAS') ):
               servidor = LayoutAtos.atos_nomeacoes(self, buffer_local, Detalhe)
               util = Util()
               ato = Ato()
               
               for i in range(len(servidor)):
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao  
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes.replace(' ', ''))
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) #vER ESTA REGRA!!!!!
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'NOMEAR   ',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'NOMEAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
                   print("RESOLUÇÕES COMPOSTAS->NOMEACAO")
 
               servidor = LayoutAtos.atos_designacoes(self, buffer_local, Detalhe)
               ato = Ato()
               for i in range(len(servidor)):
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes.replace(' ', ''))
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) #vER ESTA REGRA!!!!!
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'DESIGNAR ',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'DESIGNAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
                   print("RESOLUÇÕES COMPOSTAS->DESIGNACOES")
              
               servidor = LayoutAtos.atos_dispensas(self, buffer_local, Detalhe)
               ato = Ato()
               util = Util()
               for i in range(len(servidor)):
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes.replace(' ', ''))
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) #vER ESTA REGRA!!!!!
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'DISPENSAR',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'DISPESAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
                   print("RESOLUÇÕES COMPOSTAS->DISPENSAS")

               servidor = LayoutAtos.atos_exoneracoesTeste(self, buffer_local, Detalhe)
               ato = Ato()
               util = Util()
               for i in range(len(servidor)):
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao                   
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes)
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) #vER ESTA REGRA!!!!!
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'EXONERAR ',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'EXONERAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
              
       ######################## RESOLUÇÃO SIMPLES ########################### 
              
            elif ((resolucao1.group('resolucao1') == 'RESOLUÇÃO') or (resolucao1.group('resolucao1') == 'RESOLUÇAO') or (resolucao1.group('resolucao1') == 'RESOLUCAO') or (resolucao1.group('resolucao1') == 'DECRETO RIO') or (resolucao1.group('resolucao1') == 'PORTARIA')):
               servidor = LayoutAtos.atos_nomeacao(self, buffer_local, Detalhe, train_data)
               for i in range(len(servidor)):
                   ato = Ato()
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes)
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) #vER ESTA REGRA!!!!!
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'NOMEAR   ',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'NOMEAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
                   print("RESOLUÇÕES SIMPLES->NOMEACAO")

               servidor = LayoutAtos.atos_dispensar(self, buffer_local, Detalhe, train_data)
               for i in range(len(servidor)):
                   ato = Ato()
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes)
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) 
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'DISPENSAR',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'DISPENSAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
                   print("RESOLUÇÕES SIMPLES->DISPENSA")

               servidor = LayoutAtos.atos_exonerar(self, buffer_local, Detalhe, train_data)
               for i in range(len(servidor)):
                   ato = Ato()
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes)
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) #vER ESTA REGRA!!!!!
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'EXONERAR ',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'EXONERAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
                   print("RESOLUÇÕES SIMPLES->EXONERAR")

               servidor = LayoutAtos.atos_designar(self, buffer_local, Detalhe, arqres, train_data)  
               for i in range(len(servidor)):
                   ato = Ato()
                   ato.nome = '{: <50}'.format((servidor[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   ato.numero = '{:0>4}'.format(servidor[i].numero)
                   ato.diaResolucao = '{:0>2}'.format(servidor[i].diaResolucao)
                   ato.mesResolucao = '{:0>2}'.format(servidor[i].mesResolucao)
                   ato.anoResolucao = servidor[i].anoResolucao
                   ato.dataResolucao = ato.diaResolucao+'/'+ato.mesResolucao+'/'+ato.anoResolucao
                   ato.dia = '{:0>2}'.format(servidor[i].dia)
                   ato.mes = util.retornaMes(servidor[i].mes)
                   ato.ano = servidor[i].ano
                   ato.dataEfeito = ato.dia+'/'+ato.mes+'/'+ato.ano
                   ato.matricula = '{: <12}'.format(servidor[i].matricula.replace('.', ''))
                   ato.cargo = '{: <48}'.format((servidor[i].cargo.upper()).replace('\n', ' ').replace('  ', ' ').replace('- ', '').strip(" "))
                   ato.CPF = '{: <13}'.format(servidor[i].CPF) #vER ESTA REGRA!!!!!
                   ato.tipocargo =  servidor[i].tipocargo
                   ato.simbolo = '{: <6}'.format(servidor[i].simbolo.replace('\n', ''))
                   print(ato.CPF, Tipo, ato.numero, ato.dataResolucao, 'DESIGNAR ',  ato.matricula, ato.nome, ato.dataEfeito, ato.cargo, ato.simbolo, ato.tipocargo, file=arq1)
                   persistencia.insert(ato.matricula, ato.nome, ato.dataResolucao, 'DESIGNAR', ato.dataEfeito, ato.cargo, ato.tipocargo, ato.simbolo)
                   print("RESOLUÇÕES SIMPLES->DESIGNAR")

####### COMISSOES ########

    def comissoes(self, buffer, arqComissoes, data_e_hora, perc, contarq, arquivo):
        print('ARQUIVO========================================================>',arquivo,'(COMISSÕES)', perc,'%' )
        ################# PROCESSA CABEÇALHO DO DIARIO ################
        diario_pattern = re.compile('Ano\s([A-Z]*)\s•\sN\w\s([0-9]*)')        
        diario_edicao = diario_pattern.search(buffer)  

        diario_suplemento_pattern = re.compile('Diário Oficial do Município do Rio de Janeiro\s\|\s\w*\s\w*\s\|\s\w*\s\w*\s\|\s(Suplemento)')
        diario_suplemento = diario_suplemento_pattern.search(buffer)
        if diario_suplemento:
           tipo = 'SUPLEMENTAR' #Suplemento
        else:
           tipo = 'NORMAL' #Normal 

        util = Util()
        diario = Diario() 
        if (diario_edicao.group(1)):               
            diario.anoromano = '{: <6}'.format(((diario_edicao.group(1))))
            diario.ano = (util.converteRomano(diario_edicao.group(1)))
            diario.numero = '{:0>6}'.format((diario_edicao.group(2)))
            diario.tipo = '{: <12}'.format((tipo))
        else:
            diario.anoromano = 'XXXXXX'
            diario.ano = 'XXXXXX'
            diario.numero = 'XXXXXX'
            diario.tipo = 'XXXXXXXXXXXX'

        print('', file=arqComissoes)
        print('(PUC-RIO/TECMF)   ::PROCESSAMENTO DO DIÁRIO::', 'ANO:', diario.ano,'No.:', diario.numero, 'TIPO:', diario.tipo, '* RIO DE JANEIRO * ARQUIVO:',arquivo, 'SEQ.:', '{:0>4}'.format(contarq), '                                             ',data_e_hora,  file=arqComissoes)
        print('', file=arqComissoes) 
            
        #############################################################
        
        resolucao_pattern = re.compile(r'^(RESOLUÇÃO|RESOLUÇAO)\s[A-Z0-9]+\sN.\s[0-9]+\sDE.*[\s|\n]+.*',re.M)
        contador = 1
        inicio = []
        bloco = []
        servidor = []
        tamanho = len(buffer)
        for resolucao in resolucao_pattern.finditer(buffer):
            inicio.append(resolucao.start())
            contador=contador + 1 
        inicio.append(tamanho)        
            

        for i in range(len(inicio)-1):
            bloco.append(inicio[i+1]-inicio[i])
            buffer_local = buffer[inicio[i]:inicio[i]+bloco[i]]
        
            
            ###### Resolução #####
            resolucao1_pattern = re.compile(r'^(?P<resolucao1>RESOLUÇÃO|RESOLUÇAO)\s(?P<detalhe_resolucao1>[A-Z0-9]+\sN.\s[0-9]+\sDE.*)[\s|\n]+.*',re.M)
            resolucao1 = resolucao1_pattern.search(buffer_local)
           
            if (resolucao1):
                Tipo = '{: <09}'.format(resolucao1.group('resolucao1'))
                Detalhe = resolucao1.group('detalhe_resolucao1')
            else:
                #print('Não casou resolucao1')
                Tipo = 'SEM TIPO'
                Detalhe = 'SEM DETALHE'
            #####################            
            
            #### Gestor #####
            gestor_pattern = re.compile(r'(?P<gestor>[O|A]*\s(SECRETÁRI[O|A]+|PROCURADOR[A]*|PREFEITO[A]*|COORDENADOR[A]*)[A-ZÁÚÍÃÓÇÊÉ\s-]+)')
            gestor = gestor_pattern.search(buffer_local)
            if (gestor):
                Gestor = gestor.group('gestor')
            else:
                Gestor = 'SEM GESTOR'
            ###### Fim Gestor

            #### Cabeçalho da Comisssão técnica #####
            comissao_pattern = re.compile(r'(Institui|Designa)\s* [A-Za-zã\sé-]*\s*\((?P<tipoComissao>CTA)\)[.ºA-Za-zã\sçõé-]*\s*(?P<processo>[.\/0-9]*)[.ºA-Z\s*a-zã]*[,]*\s*[.ºA-Z\s*a-zã]*(?P<contrato>[./0-9]*)\s*\((?P<desccontrato>[a-zA-Z\s0-9.-–-]*)')
            comissao = comissao_pattern.search(buffer_local)
            Detalhe3 = ''
            if (comissao):
                Detalhe3 = '<tipoComissao>'+comissao.group('tipoComissao')+'<numprocesso>'+comissao.group('processo')+'<numcontrato>'+comissao.group('contrato')+'<desccontrato>'+comissao.group('desccontrato')

            #### Detalhes da Comissão #####]
          
            comissao1_pattern = re.compile(r'Art.\s[1-2]+.\sDesignar os membros abaixo indicados para comporem a (?P<nomeComissao>[A-ZÉÁÍÓÚÇÃÊÔÕÀÜa-záêéóíçãâôú\-\n\s\–]+)[\-|\–]*\sCONVÊNIO\sN\w\s(?P<convenio>[0-9\/]+)\n*\s*Titulares\n*\s*Órgão\s*Nome\s*Matrícula\n*')
            comissao2_pattern = re.compile(r'Art.\s[1-2]+.\sDesignar os membros abaixo indicados para comporem a (?P<nomeComissao>[A-ZÉÁÍÓÚÇÃÊÔÕÀÜa-záêéóíçãâôú\-\n\s\–]+):\n*\s*Titulares\n*\s*Órgão\s*Nome\s*Matrícula\n*')
            
            comissao1 = comissao1_pattern.search(buffer_local)
            comissao2 = comissao2_pattern.search(buffer_local)
            Detalhe2 = ''

            if (comissao1):
                Detalhe2 = '<NomeComissao>'+comissao1.group('nomeComissao')+'<ConvenioComissao>'+comissao1.group('convenio')
            
            if (comissao2):
                Detalhe2 = '<NomeComissao>'+comissao1.group('nomeComissao')+'<ConvenioComissao>'+'0000'
             
          ###### Fim Gestor
            
         ################################# RESOLUÇÕES COMPOSTAS #############################
           
            if ((resolucao1.group('resolucao1') == '*RESOLUÇÕES') or (resolucao1.group('resolucao1') == 'RESOLUÇÕES') or (resolucao1.group('resolucao1') == 'RESOLUÇOES') or (resolucao1.group('resolucao1') == 'RESOLUCOES') or (resolucao1.group('resolucao1') == 'PORTARIAS') ):
               print(resolucao1.group('resolucao1'))
 
        ######################## RESOLUÇÃO SIMPLES ########################### 
              
            elif ((resolucao1.group('resolucao1') == 'RESOLUÇÃO') or (resolucao1.group('resolucao1') == 'RESOLUÇAO') or (resolucao1.group('resolucao1') == 'RESOLUCAO') or (resolucao1.group('resolucao1') == 'DECRETO RIO') or (resolucao1.group('resolucao1') == 'PORTARIA')):

               ####### COMISSÃO ###############
               persistencia = Persistencia()
               comiss = LayoutAtos.atos_criar_comissao(self, buffer_local, Detalhe, Detalhe2, Detalhe3)
               for i in range(len(comiss)):
                   comissoes = Comissoes()
                   comissoes.tipoComissao = comiss[i].tipoComissao
                   comissoes.numero = '{:0>4}'.format(comiss[i].numero)
                   comissoes.diaResolucao = '{:0>2}'.format(comiss[i].diaResolucao)
                   comissoes.mesResolucao = '{:0>2}'.format(comiss[i].mesResolucao)
                   comissoes.anoResolucao = comiss[i].anoResolucao
                   comissoes.dataResolucao = comissoes.diaResolucao+'/'+comissoes.mesResolucao+'/'+comissoes.anoResolucao
                   comissoes.nomeComissao = '{: <68}'.format(comiss[i].nomeComissao.replace('\n', ' ').replace('  ', ' '))
                   comissoes.orgao = '{: <10}'.format(comiss[i].orgao)
                   comissoes.numContrato = comiss[i].numContrato  
                   comissoes.descContrato = comiss[i].descContrato
                   comissoes.numProcesso = comiss[i].numProcesso
                   comissoes.nome = '{: <43}'.format((comiss[i].nome).replace('\n', ' ').replace('  ', ' ').strip(" "))
                   comissoes.matricula = '{: <13}'.format(comiss[i].matricula)
                   persistencia.insertComissoes(comissoes.tipoComissao, comissoes.numero, comissoes.dataResolucao, comissoes.nomeComissao, comissoes.orgao, comissoes.numContrato, comissoes.numProcesso, comissoes.descContrato, comissoes.nome, comissoes.matricula)
        

    def do_nomeacao(self, buffer, arquivo):
  
        
        resolucao_pattern = re.compile(r'(RESOLUÇÃO|DECRETO RIO)\s*“P”\sN\w*\s*(\d+)\s*DE\s*(\d+)\s*DE\s*([A-Z]+)\s*DE\s*(\d+)\s*')
        resolucao = resolucao_pattern.search(buffer)
        
        contador = 1
        while (resolucao):
            contador = contador + 1
            ind_headergestor = resolucao.end()
            buffer = buffer[ind_headergestor:]
            header_gestor_pattern = re.compile(r'((?:.|\n.)+)\n\n')
            header_gestor = header_gestor_pattern.search(buffer)
            if header_gestor:
                print("========= Gestor ==========") 
                print(header_gestor.group(1))
            else: print("NÃO Casou gestor")
            ind_content = header_gestor.end()
            buffer = buffer[ind_content:]

            resolucao1_pattern = re.compile(u'(?P<acao>Nomear)')
            
            resolucao = resolucao1_pattern.search(buffer)
            if resolucao:
                print("===Atribuicao====")
                print('Ação->'+resolucao.group('acao'))
                ind_next_buffer_position = resolucao.end()
            else: print("NAO CASOU ATRIBUICAO")
            buffer = buffer[ind_next_buffer_position:] 
            resolucao = resolucao_pattern.search(buffer)
        print("Não Casou Resolução")
