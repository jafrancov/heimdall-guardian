import React from 'react';

export function Comentario({ cuerpo }: { cuerpo: string }) {
  return <div className="comentario" dangerouslySetInnerHTML={{ __html: cuerpo }} />;
}
