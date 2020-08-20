import React from 'react';

export default {
  title: 'Attributes/Typography',
};

export const Typography = () => {
  return (
    <>
      <h1>Headings</h1>
      <hr />
      <h1>Raw h1</h1>
      <h2>Raw h2</h2>
      <h3>Raw h3</h3>
      <h4>Raw h4</h4>
      <h5>Raw h5</h5>
      <h6>Raw h6</h6>
      <hr />
      <h1 className="title-1">Heading with .title-1</h1>
      <h1 className="title-2">Heading with .title-2</h1>
      <h1 className="title-3">Heading with .title-3</h1>
      <h1 className="subtitle-1">Heading with .subtitle-1</h1>
      <h1 className="subtitle-2">Heading with .subtitle-2</h1>
      <h1 className="subtitle-3">Heading with .subtitle-3</h1>
    </>
  );
};

Typography.story = {
  name: 'Headings',
};

export const Body = () => {
  return (
    <>
      <h1>Body</h1>
      <hr />
      <p>Raw p</p>
      <hr />
      <p className="body-1">Paragraph with .body-1</p>
      <p className="body-2">Paragraph with .body-2</p>
      <p className="body-3">Paragraph with .body-3</p>
      <p className="body-secondary-3">Paragraph with .body-secondary-3</p>
      <p className="body-placeholder">Paragraph with .body-placeholder</p>
      <p className="body-link">Paragraph with .body-link</p>
      <p className="caption">Paragraph with .caption</p>
      <p className="column-name">Paragraph with .column-name</p>
      <p className="resource-type">Paragraph with .resource-type</p>
      <p className="helper-text">Paragraph with .helper-text</p>
      <p className="text-placeholder">Paragraph with .text-placeholder</p>
      <p className="text-secondary">Paragraph with .text-secondary</p>
      <p className="text-primary">Paragraph with .text-primary</p>
    </>
  );
};

Body.story = {
  name: 'Body Text',
};
