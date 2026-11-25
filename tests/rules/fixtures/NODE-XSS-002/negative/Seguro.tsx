import React from 'react';
import DOMPurify from 'dompurify';

export function Aviso({ cuerpo }: { cuerpo: string }) {
  return <p>{cuerpo}</p>;
}

export function Rico({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />;
}

export function Fijo() {
  return <div dangerouslySetInnerHTML={{ __html: '<b>Listo</b>' }} />;
}
