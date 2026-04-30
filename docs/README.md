# Generate diagrams
https://docs.structurizr.com/export

brew install ruby
echo 'export PATH="/opt/homebrew/opt/ruby/bin:$PATH"' >> ~/.bash_profile
echo 'export PATH="/opt/homebrew/lib/ruby/gems/4.0.0/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile

brew install structurizr-cli
structurizr-cli version
structurizr-cli validate -workspace digital-twin.dsl

mkdir -p diagrams
structurizr-cli  export -workspace digital-twin.dsl -format plantuml/structurizr -output diagrams

# View diagrams
brew install asciidoctor
brew install plantuml
gem install asciidoctor-diagram asciidoctor-diagram-plantuml

asciidoctor \
  -r asciidoctor-diagram \
  03_context_and_scope.adoc

open 03_context_and_scope.html

# View pdf

gem install asciidoctor-pdf

asciidoctor-pdf -r asciidoctor-diagram digital-twin.adoc

