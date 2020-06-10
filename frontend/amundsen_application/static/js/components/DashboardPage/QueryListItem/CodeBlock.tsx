import * as React from 'react';
import { CopyBlock, atomOneLight } from 'react-code-blocks';

const LANGUAGE = 'sql';

type CodeBlockProps = {
  text: string;
};

const CodeBlock: React.SFC<CodeBlockProps> = ({ text }: CodeBlockProps) => {
  return (
    <CopyBlock
      text={text}
      language={LANGUAGE}
      theme={atomOneLight}
      showLineNumbers={false}
      wrapLines
      codeBlock
    />
  );
};

export default CodeBlock;
