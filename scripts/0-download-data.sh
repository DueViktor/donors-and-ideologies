poetry shell
poetry install

# Download and rename Littlesis entities and relationships data
for file in "entities" "relationships"; do
    wget -O "data/littlesis_${file}.json.gz" "https://littlesis.org/public_data/${file}.json.gz" && \
    gunzip "data/littlesis_${file}.json.gz" && \
    mv "data/littlesis_${file}.json" "data/littlesis-${file}.json"
done

# Download legislators-historical.yaml data from the GitHub repository
wget -O data/legislators-historical.yaml https://github.com/unitedstates/congress-legislators/raw/main/legislators-historical.yaml

python scripts/yaml-to-json.py data/legislators-historical.yaml data/legislators-historical.json

rm data/legislators-historical.yaml