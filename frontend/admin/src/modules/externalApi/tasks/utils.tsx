import { Tag, Badge } from 'antd';
import { SyncOutlined, DatabaseOutlined, DollarOutlined, RiseOutlined } from '@ant-design/icons';

const taskTypeColors: Record<string, string> = {
  prices: 'blue',
  stats: 'green',
  markets: 'orange',
  default: 'default',
};

const taskTypeIcons: Record<string, React.ReactElement> = {
  prices: <DollarOutlined />,
  stats: <DatabaseOutlined />,
  markets: <RiseOutlined />,
  default: <SyncOutlined />,
};

export const getTaskTypeTag = (type: string): React.ReactElement => {
  const color = taskTypeColors[type] || taskTypeColors.default;
  const icon = taskTypeIcons[type] || taskTypeIcons.default;
  return <Tag icon={icon} color={color}>{type}</Tag>;
};

export const getStatusBadge = (status: boolean): React.ReactElement => {
  return status ? (
    <Badge status="success" text="Активна" />
  ) : (
    <Badge status="error" text="Неактивна" />
  );
};

/**
 * Преобразует строку с синтаксисом, похожим на Markdown (жирный шрифт, курсив, код), в элементы React.
 * Избегает использования dangerouslySetInnerHTML, создавая элементы React напрямую.
 */
const parseInlineFormat = (text: string): React.ReactNode[] => {
  const parts: React.ReactNode[] = [];
  let remaining = text;
  let keyIndex = 0;

  while (remaining.length > 0) {
    // Inline code `...`
    const codeMatch = remaining.match(/`([^`]+)`/);
    if (codeMatch && codeMatch.index !== undefined) {
      if (codeMatch.index > 0) {
        parts.push(remaining.slice(0, codeMatch.index));
      }
      parts.push(
        <code key={keyIndex++} style={{ background: 'var(--code-bg)', padding: '2px 4px', borderRadius: '3px' }}>
          {codeMatch[1]}
        </code>,
      );
      remaining = remaining.slice(codeMatch.index + codeMatch[0].length);
      continue;
    }

    // Bold **...**
    const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
    if (boldMatch && boldMatch.index !== undefined) {
      if (boldMatch.index > 0) {
        parts.push(remaining.slice(0, boldMatch.index));
      }
      parts.push(<strong key={keyIndex++}>{boldMatch[1]}</strong>);
      remaining = remaining.slice(boldMatch.index + boldMatch[0].length);
      continue;
    }

    // Italic *...*
    const italicMatch = remaining.match(/(?<!\*)\*([^*]+)\*(?!\*)/);
    if (italicMatch && italicMatch.index !== undefined) {
      if (italicMatch.index > 0) {
        parts.push(remaining.slice(0, italicMatch.index));
      }
      parts.push(<em key={keyIndex++}>{italicMatch[1]}</em>);
      remaining = remaining.slice(italicMatch.index + italicMatch[0].length);
      continue;
    }

    parts.push(remaining);
    break;
  }

  return parts;
};

export const formatDescription = (text: string | null | undefined): React.ReactNode => {
  if (!text) return null;

  const lines = text.split('\n');
  return lines.map((line, index) => {
    // Headings
    if (line.startsWith('## ')) {
      return (
        <h4 key={index} style={{ margin: '8px 0 4px 0', color: '#0050b3' }}>
          {parseInlineFormat(line.slice(3))}
        </h4>
      );
    }
    if (line.startsWith('### ')) {
      return (
        <h5 key={index} style={{ margin: '6px 0 3px 0', color: '#0050b3' }}>
          {parseInlineFormat(line.slice(4))}
        </h5>
      );
    }

    // Lists
    if (line.match(/^[\-\*]\s/)) {
      return (
        <li key={index} style={{ marginLeft: '20px' }}>
          {parseInlineFormat(line.slice(2))}
        </li>
      );
    }
    if (line.match(/^\d+\.\s/)) {
      return (
        <li key={index} style={{ marginLeft: '20px' }}>
          {parseInlineFormat(line)}
        </li>
      );
    }

    // Empty lines
    if (line.trim() === '') {
      return <br key={index} />;
    }

    return (
      <div key={index}>
        {parseInlineFormat(line)}
      </div>
    );
  });
};
