"""Lecture YAML et validation du sous-ensemble du schéma utilisé par le dépôt."""
from datetime import date
import json
from pathlib import Path
import re

try:
    import yaml
except ImportError as exc:
    raise SystemExit('PyYAML manque : python3 -m pip install -r scripts/requirements.txt') from exc

ROOT = Path(__file__).resolve().parents[1]

class Loader(yaml.SafeLoader):
    pass

# Conserver les dates ISO comme chaînes, comme dans le schéma JSON.
Loader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in values if tag != 'tag:yaml.org,2002:timestamp']
    for key, values in Loader.yaml_implicit_resolvers.items()
}

def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise ValueError('Les clés YAML doivent être des chaînes')
        if key in result:
            raise ValueError(f'Clé YAML dupliquée : {key}')
        result[key] = loader.construct_object(value_node)
    return result

Loader.add_constructor('tag:yaml.org,2002:map', mapping)

KEYWORDS = {'$schema', '$id', 'title', 'description', 'type', 'required', 'properties',
            'additionalProperties', 'enum', 'minLength', 'pattern', 'format',
            'items', 'minItems', 'uniqueItems', 'minimum'}
TYPES = {'object': lambda x: isinstance(x, dict), 'array': lambda x: isinstance(x, list),
         'string': lambda x: isinstance(x, str), 'integer': lambda x: type(x) is int,
         'boolean': lambda x: type(x) is bool}

def check_schema(schema):
    if not isinstance(schema, dict):
        raise ValueError('Chaque schéma doit être un objet JSON')
    if 'additionalProperties' in schema and type(schema['additionalProperties']) is not bool:
        raise ValueError('additionalProperties doit être un booléen')
    for key in schema:
        if key not in KEYWORDS and not key.startswith('x-'):
            raise ValueError(f'Contrainte JSON Schema non prise en charge : {key}')
    if 'type' in schema and schema['type'] not in TYPES:
        raise ValueError(f'Type du schéma non pris en charge : {schema["type"]}')
    if 'format' in schema and schema['format'] != 'date':
        raise ValueError('Seul le format date est pris en charge')
    for sub in schema.get('properties', {}).values():
        check_schema(sub)
    if 'items' in schema:
        check_schema(schema['items'])

def load_schema():
    schema = json.loads((ROOT / '_schemas/ressource.schema.json').read_text())
    check_schema(schema)
    return schema

def validate(value, schema, location='métadonnées'):
    errors = []
    def error(message):
        errors.append(f'{location} : {message}')
    if 'type' in schema and not TYPES[schema['type']](value):
        return [f'{location} : type attendu {schema["type"]}']
    if 'enum' in schema and value not in schema['enum']:
        error(f'valeur autorisée parmi {schema["enum"]}')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                error(f'champ obligatoire absent : {key}')
        for key, item in value.items():
            if key in schema.get('properties', {}):
                errors.extend(validate(item, schema['properties'][key], f'{location}.{key}'))
            elif schema.get('additionalProperties') is False:
                error(f'champ inconnu : {key}')
    if isinstance(value, str):
        if len(value.strip()) < schema.get('minLength', 0):
            error('chaîne vide ou trop courte')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            error('syntaxe invalide')
        if schema.get('format') == 'date':
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError()
                date.fromisoformat(value)
            except ValueError:
                error('date ISO YYYY-MM-DD invalide')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            error('liste trop courte')
        if schema.get('uniqueItems') and any(item in value[:i] for i, item in enumerate(value)):
            error('éléments dupliqués')
        for i, item in enumerate(value):
            if 'items' in schema:
                errors.extend(validate(item, schema['items'], f'{location}[{i}]'))
    if type(value) is int and value < schema.get('minimum', value):
        error(f'minimum : {schema["minimum"]}')
    return errors

def read_source(path):
    text = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', text, re.S)
    if not match:
        raise ValueError('En-tête YAML absent ou non fermé')
    metadata = yaml.load(match.group(1), Loader=Loader)
    return metadata, text[match.end():], text[:match.end()].count('\n') + 1
