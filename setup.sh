#!/bin/bash
export LLM_PROVIDER=azure_openai
export LLM_ENDPOINT=bla-bla
export LLM_API_KEY=un_super_secreto
export GITHUB_TOKEN=otro_super_secreto
# correr desde app | si no poner prompts y correr desde tests
export PROMPT_FILE=boton/tests/prompts.yml
# correr dentro del contenedor
export GITHUB_REPOSITORY=pruebas