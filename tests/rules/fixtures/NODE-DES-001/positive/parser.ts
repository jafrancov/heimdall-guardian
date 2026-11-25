import * as yaml from 'js-yaml';

export function cargar(texto: string) {
  return yaml.loadAll(texto, undefined, { schema: yaml.DEFAULT_FULL_SCHEMA });
}
