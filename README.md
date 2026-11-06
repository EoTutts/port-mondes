# Port Mondes

Porte acessível do RPG Port Mondes, com exploração, combates por turnos, inventário, magia e aventuras em português, inglês e francês.

Este é o repositório de distribuição dos pacotes preparados no projeto R36S. A versão interna do jogo é **0.1.0**; a release de distribuição é de 06/11/2026.

## Baixar

[Pacote R36S ARM64](https://github.com/EoTutts/port-mondes/releases/download/v0.1.0-distribution.20261106/port-mondes-linux-arm64.zip) · [Release e SHA-256](https://github.com/EoTutts/port-mondes/releases/tag/v0.1.0-distribution.20261106)

## Requisitos e estado

Luma/ArkOS em R36S **RK3326, Linux ARM64**, com as bibliotecas de áudio e vídeo da plataforma. Inclui Python 3.8 privado para o bytecode original. Não é um pacote para GA36/ARMv7. Distribuição experimental. O pacote foi compilado para Linux ARM64; a validação física desta revisão no console permanece pendente.

## Instalar ou atualizar

Extraia o ZIP inteiro e copie a pasta `port-mondes` para `a11y/games/` na partição EASYROMS do cartão. O `game.json` deve ficar diretamente dentro dessa pasta. Com Luma ligado, a lista reconhece o jogo automaticamente. Também é possível enviar o ZIP pela opção Instalar jogo da Página no PC do Luma. Feche o jogo antes de atualizar; preserve a pasta `a11y/saves/`.

## Controles

Direcional navega; B confirma; A volta; Start pausa; Select repete. X abre inventário; L/R e gatilhos abrem as consultas do personagem. Fn, Power e volume continuam reservados ao sistema.

## Arquivos e salvamentos

O pacote foi conferido quanto ao manifesto, executável e SHA-256. Não acompanha salvamentos, preferências pessoais ou registros de testes. Os saves ficam na pasta de dados atribuída pelo Luma, normalmente `a11y/saves/port-mondes/`. Esta publicação não representa uma nova campanha completa ou teste físico.

## Créditos e licenças

Preserva bytecode, textos, arte e sons do jogo original. A distribuição não altera a titularidade desses materiais; os adaptadores e bibliotecas mantêm seus próprios avisos. Os avisos de terceiros presentes no pacote devem ser mantidos. Não se atribui uma licença única a todo o conteúdo.
