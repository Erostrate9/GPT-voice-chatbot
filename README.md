# instructions

## frontend

Change directory into frontend

```shell
cd ..
cd chatbot/frontend
```

Install packages

```shell
yarn --exact
```

Build application

```shell
yarn build
```

Start server in dev mode

```shell
yarn dev
```

You can check your dev server is working by going to:

```plain
http://localhost:5173/health
```

or alternatively in live mode:

```shell
yarn start
```

You can check your live server is working by going to:

```plain
http://localhost:4173/health
```

## backend

### Start your backend server

Start your backend server

```shell
uvicorn main:app
```

Alternatively, you can ensure your server resets every time you make a change by typing:

```shell
uvicorn main:app -- reload
```

# backend

## ASR

## intent detection

## actions

### Create Meal Plan



### Calculate food calories



### Recommend recipes based on ingredients



### Describe recipe



## TTS

# frontend

