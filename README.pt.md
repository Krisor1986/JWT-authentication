# Star Wars Blog — Autenticação JWT

[English](README.md) · [Español](README.es.md) · [Português](README.pt.md)

Exercício final de autenticação da 4Geeks Academy, baseado no template oficial React + Flask. Reutiliza o código do Star Wars Blog e da Star Wars API neste repositório separado.

## Fluxo exigido

- `/signup`: cria um usuário com e-mail e senha e redireciona para `/login`.
- `/login`: valida as credenciais, salva o JWT no `sessionStorage` e redireciona para `/private`.
- `/private`: valida o token com o Flask antes de mostrar os favoritos. Revalida a cada 30 segundos e quando a janela recupera o foco. Sessões inválidas ou expiradas redirecionam para `/login`.
- Logout na navbar: remove o token, limpa os favoritos e redireciona para `/login`.

Catálogo e detalhes são públicos. Clicar na estrela sem estar conectado abre o login. Os favoritos pertencem ao usuário autenticado e ficam salvos no banco. O backend identifica o usuário pelo JWT assinado; `X-User-ID` não permite escolher outra conta. As senhas são hashes do Werkzeug e nunca são devolvidas. Os tokens expiram após 30 minutos. Logout limpa a sessão do navegador; este exercício não implementa revogação do token no servidor.

## Configuração local

Use Python 3.13, Pipenv e Node.js 20.19+ ou 22.12+. Este projeto local já tem dependências, `.env`, migrações e catálogo configurados. Os passos abaixo são para um clone novo; preserve seu `.env` ao continuar.

```bash
pipenv install
npm install
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Substitua `JWT_SECRET_KEY` no `.env` pelo valor aleatório gerado. Não envie `.env` ao GitHub. SQLite é o banco local padrão e não precisa de um serviço separado.

Backend em um terminal:

```bash
pipenv run upgrade
pipenv run flask seed
pipenv run start
```
React em outro terminal:

```bash
npm run start
```
Abra [o frontend](http://localhost:3000). O Flask roda em `http://127.0.0.1:3001`, configurado em `VITE_BACKEND_URL`. O seed pode ser repetido e importa os mesmos 10 personagens, 10 planetas e 10 veículos do exercício anterior. Crie sua conta em `/signup`.

## API

| Método | Endpoint | Autenticação |
| --- | --- | --- |
| POST | `/api/signup` | Público |
| POST | `/api/login` | Público |
| GET | `/api/private` | Bearer JWT |
| GET | `/api/people`, `/api/planets`, `/api/vehicles` | Público |
| GET | `/api/<category>/<id>` | Público |
| GET | `/api/users/favorites` | Bearer JWT |
| POST / DELETE | `/api/favorite/<category>/<id>` | Bearer JWT |

As categorias são `people`, `planets` e `vehicles`. As rotas usam IDs locais do banco; as imagens usam o `swapi_id` separado, sem presumir que coincidem. Cadastro e login recebem JSON com `email` e `password`.

## Verificação

```bash
pipenv run test
npm run lint
npm run build
```
Os testes verificam autenticação, hashes, tokens inválidos e expirados, migrações, importação repetível e isolamento de favoritos. A integração usa um servidor HTTP real e SQLite isolado, sem simular respostas. O fluxo com frontend e backend também foi conferido no navegador. As 30 URLs externas de imagens responderam com imagens durante a verificação; sua disponibilidade pode mudar.

## Fontes e escopo

- [Enunciado de autenticação](https://github.com/breatheco-de/jwt-authentication-with-flask-react).
- [Template oficial](https://github.com/4GeeksAcademy/react-flask-hello).
- Exercícios reutilizados: Starwars-blog e Starwars-blog-api; os originais foram preservados.
- `data/starwars.json` preserva a captura da SWAPI.tech e os nomes relacionados do exercício anterior. O frontend consulta a API Flask local, não a SWAPI.tech diretamente.
- As imagens vêm do [repositório swapi-images da escola](https://github.com/breatheco-de/swapi-images).

O painel admin sem proteção e a listagem pública de usuários do template não estão registrados. O escopo é a autenticação, sem recuperação de contas ou implantação adicional em produção. O backend pode servir o build do React após `npm run build`.
