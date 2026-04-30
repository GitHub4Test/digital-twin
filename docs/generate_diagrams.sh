#!/bin/bash

structurizr-cli validate -workspace digital-twin.dsl

rm -rf diagrams
mkdir -p diagrams
structurizr-cli  export -workspace digital-twin.dsl -format plantuml/structurizr -output diagrams

cd diagrams

for f in structurizr-*; do
  mv "$f" "${f#structurizr-}"
done

cd ..
asciidoctor-pdf -r asciidoctor-diagram digital-twin.adoc


