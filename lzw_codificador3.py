# -*- coding: utf-8 -*-

import sys
from time import time
from bitarray import *
from math import *

#Essa funcao eh o compressor LZW.
#Recebe como entradas:
#   dados_entrada = Uma lista de Bytes que serao comprimidos
#   tam_max = O numero maximo de bits do dicionario
def compressor(dados_entrada,tam_max):
    #Informações para esse compressor especifico
    escalador = 0 #Variavel que vai medir a variacao do Comprimento Medio
    
    #Aqui sera decidido onde esta o limite do escalador (Explicacao desses numeros no relatorio)
    if tam_max == 12:
        tam_limite_escalador = 0.01
    elif tam_max == 15:
        tam_limite_escalador = 0.004
    elif tam_max == 18:
        tam_limite_escalador = 0.002
    elif tam_max == 21:
        tam_limite_escalador = 0.001
    

    #Informacoes para gerar o dicionario
    tam_max_dict = pow(2,tam_max) 
    dictionary_size = 256 #O tamanho inicial dele
    tam_bits = 8 #O tanto de bits necessario para esse tamanho inicial
    dictionary = {bytes([i]):i for i in range(dictionary_size)} #O dicionario em si

    result = bitarray() #Aqui sera colocado os bits da compressao
    comprimento_medio = [] #Aqui sera um dicionario de todos os comprimentos medios do arquivo com os respectivos comprimentos atuais do arquivo
    comprimento_total = 0 #Essa variavel guarda o comprimento atual do arquivo
    
    current = b'' #Essa Variavel sera util para guardar a string de bytes que esta sendo procurada no dicionario

    for byte in dados_entrada:

        #Logica LZW para compressao
        new_string = current + bytes([byte])
        
        if new_string in dictionary:
            current = new_string
        else:
            result.extend(format(dictionary[current],'b').zfill(tam_bits))
            comprimento_medio.append(len(result)/comprimento_total) #Salva na lista o comprimento medio quando ele foi comprimir

            if len(dictionary) < tam_max_dict:
                dictionary[new_string] = dictionary_size
                dictionary_size += 1

                if len(dictionary) >= pow(2,tam_bits):
                    tam_bits +=1   
            else:
                i = len(comprimento_medio)-1

                #Calcula usando predicao de ordem 2 do proximo termo
                predicao = 2*comprimento_medio[i] - comprimento_medio[i-1]
                escalador += predicao - comprimento_medio[i] #E verifica se esta crescente ou decrescente

                #Para esse codigo, a descida nao importa, apenas quando sobe o escalador
                if escalador < 0:
                    escalador = 0
                elif escalador >= tam_limite_escalador: #Se ele chegar no limite estabelecido

                    #Reinicia o dicionario, com os valores iniciais
                    escalador = 0
                    dictionary_size = 256
                    tam_bits = 8
                    dictionary = {bytes([i]):i for i in range(dictionary_size)}
                
            current = bytes([byte])

            
        comprimento_total +=1
        
        
    #Codifica o ultimo elemento do arquivo
    if current:
        result.extend(format(dictionary[current],'b').zfill(tam_bits))
        comprimento_medio.append(len(result)/comprimento_total) #Calcula seu comprimento medio

    #Retorna tanto os bits da compressao quanto a lista de comprimentos medios
    return result,comprimento_medio

#Essa funcao eh o descompressor LZW.
#Recebe como entradas:
#   dados_comprimidos = Um bitarray dos dados comprimidos
#   tam_max = O numero maximo de bits do dicionario
#   tam_arq_compress = Tamanho do arquivo comprimido 
def decompress(dados_comprimidos, tam_max, tam_arq_compress):  
    #Informações para esse compressor especifico
    escalador = 0 #Variavel que vai medir a variacao do Comprimento Medio
    
    #Aqui sera decidido onde esta o limite do escalador (Explicacao desses numeros no relatorio)
    if tam_max == 12:
        tam_limite_escalador = 0.01
    elif tam_max == 15:
        tam_limite_escalador = 0.004
    elif tam_max == 18:
        tam_limite_escalador = 0.002
    elif tam_max == 21:
        tam_limite_escalador = 0.001
    
    first_element = True #Flag para indicar se eh o primeiro elemento ou nao

    #Informacoes para gerar o dicionario
    tam_max_dict = pow(2,tam_max) 
    dictionary_size = 256 #O tamanho inicial dele
    tam_bits = 8 #O tanto de bits necessario para esse tamanho inicial
    dictionary = {i: bytes([i]) for i in range(dictionary_size)} #O dicionario em si
    escalador = 0

    result = [] #Lista indicando os bytes descomprimidos
    comprimento_medio = [] #Aqui sera uma de todos os comprimentos medios do arquivo com os respectivos comprimentos atuais do arquivo
    comprimento_total = 0

    idx = 0  # Contador de quantos bits ja foram no arquivo

    while idx < tam_arq_compress:
        code = dados_comprimidos[idx:idx+tam_bits].to01()
        idx += tam_bits
        code = int(code, 2)

        #Primeiro elemento
        if first_element == True:
            #Decodifica a entrada e coloca na saida
            saida = dictionary[code]
            result.append(saida)

            #Calcula o Comprimento Medio
            comprimento_total += len(saida)
            comprimento_medio.append(idx/comprimento_total)

            #Adiciona ao dicionario com o final incompleto
            if(len(dictionary) < tam_max_dict):
                dictionary[dictionary_size] = saida
       
                if len(dictionary) >= pow(2,tam_bits):
                    tam_bits +=1
                
                first_element = False #So pra indicar que ja passou do primeiro elemento
            else:
                #Apesar de ser impossivel acontecer, mas se encher o dicionario com o primeiro elemento

                #Reinicia o dicionario com os valores iniciais
                dictionary_size = 256
                tam_bits = 8
                dictionary = {i: bytes([i]) for i in range(dictionary_size)}

                first_element = True #Indica que e o primeiro elemento do dicionario
            continue

        #Restante dos elementos

        #Decodifica o inicio do elemento
        last_byte = dictionary[code][0:1]

        #Completa o ultimo elemento do dicionario
        if(dictionary_size < tam_max_dict):
            dictionary[dictionary_size] += last_byte
            dictionary_size+=1

        #Decodifica o elemento por completo e coloca na saida
        saida = dictionary[code]
        result.append(saida)

        #Calcula o Comprimento Medio
        comprimento_total += len(saida)
        comprimento_medio.append(idx/comprimento_total)

        #Adiciona ao dicionario com o final incompleto
        if(len(dictionary) < tam_max_dict):
            dictionary[dictionary_size] = saida
       
            if len(dictionary) >= pow(2,tam_bits):
                tam_bits +=1
        else: #Caso contrario
            i = len(comprimento_medio)-1

            predicao = 2*comprimento_medio[i] - comprimento_medio[i-1]
            escalador += predicao - comprimento_medio[i] #E verifica se esta crescente ou decrescente
 
            #Para esse codigo, a descida nao importa, apenas quando sobe o escalador
            if escalador < 0:
                escalador = 0
            elif escalador >= tam_limite_escalador:
                escalador = 0

                #Reinicia o dicionario com os valores iniciais
             
                dictionary_size = 256
                tam_bits = 8
                dictionary = {i: bytes([i]) for i in range(dictionary_size)}

                first_element = True #Indica que e o primeiro elemento do dicionario

    #Retorna a lista dos elementos decodificados
    return result

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Chame: lzw_codificador2.py [input_file] [max_dict_size]")
        print("Obs -> tam_max_dictionary = 2^max_dict_size")
        sys.exit(1)

    #Recebe essas 2 variaveis na chamada de execucao
    input_file = sys.argv[1]
    tam_max = int(sys.argv[2])

    #Abre o arquivo de entrada
    with open(input_file,'rb') as file:
        data = file.read() #Le todos seus dados
    
    #Calcula o tempo da compressao
    inicio = time()
    compressed_data,comprimento_medio = compressor(data,tam_max) #Chama a compressao
    fim = time()
    
    #Calcula o tamanho do arquivo comprimido e coloca nos 5 primeiros bytes do arquivo
    tam_compressed = len(compressed_data)
    bytes_tam_compressed = tam_compressed.to_bytes(5,'big')
    
    #Da linha 170 ate 176, eh um codigo para descobrir como sera o nome do arquivo de saida
    #O arquivo de saida tem a seguinte logica (nome_arquivo_entrada)+'lzw.bin'
    split = input_file.split('.')

    #Esse if me garante arquivos sem extensao
    if len(split) == 2:
        output_file = split[0] + 'lzw.bin'
    elif len(split) == 1:
        output_file = input_file + 'lzw.bin'

    #Escreve no arquivo de saida os bytes do tamanho e os bits da compressao
    with open(output_file,'wb') as file:
        file.write(bytes_tam_compressed)
        compressed_data.tofile(file)

    #Salva num arquivo, o comprimento medio durante a compressao
    #with open("dados_comprimento_medio3.txt",'w') as file:
    #    for i in range(len(comprimento_medio)):
    #        file.write(f'{i+1}:{comprimento_medio[i]}\n')

    print(f'Demorou {fim-inicio} segundos para comprimir')
    print(f'O comprimento medio dos valores foi {comprimento_medio[len(comprimento_medio)-1]}')
    print("Compressao Concluida!!")

    #Processo de Descompressão

    #Calcula o tempo da descompressao
    inicio = time()
    uncompressed_data = decompress(compressed_data,tam_max,tam_compressed) #Chama a descompressao
    fim = time()

    #Descobre como sera o nome do arquivo de saida do descompressor
    #Nesse codigo, o arquivo de saida sera (input_file)+'uncompressed.bin'
    split = input_file.split('.')

    #Esse if me garante arquivos sem extensao
    if len(split) == 2:
        output_file = split[0] + 'uncompressed.bin'
    elif len(split) == 1:
        output_file = input_file + 'uncompressed.bin'

    #Escreve no arquivo de saida os bytes da descompressao
    with open(output_file,'wb') as file:
        for string in uncompressed_data:
            file.write(string)

    print(f'Demorou {fim-inicio} segundos para descomprimir')
    print("Descompressao Concluida!!")