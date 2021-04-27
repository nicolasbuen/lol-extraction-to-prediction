# League of Legends - da Extração à Previsão
Nesse projeto, eu utilizei a [API disponibilizada pela Riot Games](https://developer.riotgames.com/) para **criar um dataset contendo estatísticas de aproximadamente 55 mil partidas diferentes**, todas do mais alto nível do servidor brasileiro.

Realizei um notebook de exploração dos dados para entender melhor o dataset. Nele, além do EDA tradicional, aproveitei meu conhecimento sobre o jogo para explorar de forma mais "curiosa". É um notebook extremamente interessante para aqueles que entendem do jogo.

O terceiro notebook contém o processo de limpeza, padronização, normalização e criação dos sets de dados de acordo com os modelos que eu planejei utilizar.

Por fim, no quarto notebook realizei as previsões. Testei mais de 6 algoritmos em 4 datasets diferentes, com centenas de sets de hiperparâmetros testados! O resultado alcançado foi de **0.72 de acurácia no set de teste**.

Considerando a natureza do dataset e todas as possibilidades que um jogo complexo como League of Legends oferece, eu não esperava nenhum resultado extremamente elevado. Acertar o time vitorioso aos 10min em um jogo que a partida dura entre 30-45min 72% das vezes é um resultado expressivo positivamente.

Acredito que com um maior volume de dados, um cuidado maior com a área de seleção dos campeões, a adição de dados característicos de cada player (como familiaridade com o campeão escolhido, por ex.) e a adição de features que levem em consideração o meta do jogo, seria possível aumentar esse score ainda mais. No entanto, assim como o futebol, o League of Legends é uma caixinha de surpresas pois depende de muito mais do que apenas números - comunicação entre o time, empenho individual e motivação são aspectos que ainda não são possíveis de implementar em um dataset de larga escala como esse.
