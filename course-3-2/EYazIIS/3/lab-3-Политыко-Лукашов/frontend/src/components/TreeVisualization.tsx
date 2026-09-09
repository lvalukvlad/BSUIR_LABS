import { useMemo, useState } from 'react';
import { ConstituencyNode, ConstituencyTree, DependencyNode, DependencyTree } from '../api/client';

interface TreeVisualizationProps {
  dependencyTrees?: DependencyTree[];
  constituencyTrees?: ConstituencyTree[];
}

interface DrawNode<T> {
  key: string;
  node: T;
  x: number;
  y: number;
}

interface DrawEdge {
  from: string;
  to: string;
  label?: string;
}

interface DrawLayout<T> {
  nodes: Array<DrawNode<T>>;
  edges: DrawEdge[];
  width: number;
  height: number;
}

interface RectBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

const POS_COLORS: Record<string, string> = {
  NOUN: '#4CAF50',
  VERB: '#2196F3',
  ADJF: '#FF9800',
  ADVB: '#8E24AA',
  PREP: '#546E7A',
  CONJ: '#6D4C41',
  NPRO: '#3F51B5',
  INFN: '#03A9F4',
  PUNCT: '#9E9E9E',
};

const LABEL_COLORS: Record<string, string> = {
  S: '#1E88E5',
  NP: '#43A047',
  VP: '#FB8C00',
  PP: '#8E24AA',
  Punct: '#9E9E9E',
  N: '#2E7D32',
  V: '#1565C0',
  Adj: '#EF6C00',
  AdvP: '#6A1B9A',
  Prep: '#455A64',
};

function colorByPos(pos: string): string {
  return POS_COLORS[pos] || '#607D8B';
}

function colorByLabel(label: string): string {
  return LABEL_COLORS[label] || '#607D8B';
}

/** Не даём кругам раздуваться с длиной токена (внутри всё равно обрезка ~12 симв.) — иначе перекрывают блок ролей под SVG. */
const DEP_NODE_R_MIN = 22;
const DEP_NODE_R_MAX = 34;

function dependencyNodeRadius(token: string, pos = ''): number {
  const tLen = Math.min(token.length, 12);
  const fromToken = Math.ceil(18 + tLen * 1.35);
  const fromPos = pos ? Math.ceil(14 + Math.min(pos.length, 6) * 1.1) : 0;
  return Math.min(DEP_NODE_R_MAX, Math.max(DEP_NODE_R_MIN, Math.max(fromToken, fromPos)));
}

function buildDependencyLayout(root: DependencyNode | null): DrawLayout<DependencyNode> {
  if (!root) return { nodes: [], edges: [], width: 900, height: 280 };

  const nodes: Array<DrawNode<DependencyNode>> = [];
  const edges: DrawEdge[] = [];
  const yStep = 92;
  const pad = 50;
  const minGap = 24;
  let maxDepth = 0;
  const ownWidth = (node: DependencyNode) =>
    dependencyNodeRadius(node.token, node.pos || '') * 2 + minGap;

  const subtreeWidth = new Map<string, number>();

  const measure = (node: DependencyNode, key: string): number => {
    const children = [...(node.children || [])].sort((a, b) => a.id - b.id);
    const childrenWidth = children.reduce(
      (sum, child, idx) => sum + measure(child, `${key}.${idx}`),
      0
    );
    const width = Math.max(ownWidth(node), childrenWidth);
    subtreeWidth.set(key, width);
    return width;
  };

  const place = (node: DependencyNode, key: string, depth: number, left: number): void => {
    maxDepth = Math.max(maxDepth, depth);
    const currentWidth = subtreeWidth.get(key) || ownWidth(node);
    const x = left + currentWidth / 2;
    nodes.push({ key, node, x, y: pad + depth * yStep });

    const children = [...(node.children || [])].sort((a, b) => a.id - b.id);
    const childrenTotal = children.reduce(
      (sum, _child, idx) => sum + (subtreeWidth.get(`${key}.${idx}`) || 0),
      0
    );
    let childLeft = left + Math.max(0, (currentWidth - childrenTotal) / 2);

    children.forEach((child, idx) => {
      const childKey = `${key}.${idx}`;
      edges.push({
        from: key,
        to: childKey,
        label: child.relation_ru || child.relation || '',
      });
      place(child, childKey, depth + 1, childLeft);
      childLeft += subtreeWidth.get(childKey) || 0;
    });
  };

  const totalWidth = measure(root, 'root');
  place(root, 'root', 0, pad);
  const bottomExtent = DEP_NODE_R_MAX + 40;
  return {
    nodes,
    edges,
    width: Math.max(900, pad * 2 + totalWidth),
    height: Math.max(320, pad + maxDepth * yStep + bottomExtent),
  };
}

function buildConstituencyLayout(root: ConstituencyNode | null): DrawLayout<ConstituencyNode | string> {
  if (!root) return { nodes: [], edges: [], width: 900, height: 280 };

  const nodes: Array<DrawNode<ConstituencyNode | string>> = [];
  const edges: DrawEdge[] = [];
  const xStep = 108;
  const yStep = 82;
  const pad = 44;
  let leaf = 0;
  let maxDepth = 0;

  const walk = (node: ConstituencyNode | string, key: string, depth: number): number => {
    maxDepth = Math.max(maxDepth, depth);

    if (typeof node === 'string') {
      const x = pad + leaf * xStep;
      leaf += 1;
      nodes.push({ key, node, x, y: pad + depth * yStep });
      return x;
    }

    const children = node.children || [];
    if (children.length === 0) {
      const x = pad + leaf * xStep;
      leaf += 1;
      nodes.push({ key, node, x, y: pad + depth * yStep });
      return x;
    }

    const childXs = children.map((child, idx) => {
      const childKey = `${key}.${idx}`;
      edges.push({ from: key, to: childKey });
      return walk(child, childKey, depth + 1);
    });

    const x = childXs.reduce((sum, item) => sum + item, 0) / childXs.length;
    nodes.push({ key, node, x, y: pad + depth * yStep });
    return x;
  };

  walk(root, 'root', 0);
  return {
    nodes,
    edges,
    width: Math.max(900, pad * 2 + Math.max(leaf, 1) * xStep),
    height: Math.max(300, pad * 2 + (maxDepth + 1) * yStep),
  };
}

function DependencyTreeView({ tree }: { tree: DependencyTree }) {
  const layout = useMemo(() => buildDependencyLayout(tree.tree), [tree.tree]);
  const byKey = useMemo(() => Object.fromEntries(layout.nodes.map((n) => [n.key, n])), [layout.nodes]);
  const edgeLabels = useMemo(() => {
    const intersects = (a: RectBox, b: RectBox) =>
      !(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h < b.y || b.y + b.h < a.y);
    const occupied: RectBox[] = [];

    layout.nodes.forEach(({ node, x, y }) => {
      const r = dependencyNodeRadius(node.token, node.pos || '');
      occupied.push({ x: x - r - 4, y: y - r - 4, w: r * 2 + 8, h: r * 2 + 8 });
    });

    const prepared = layout.edges
      .map((edge) => {
        const from = byKey[edge.from];
        const to = byKey[edge.to];
        if (!from || !to || !edge.label) return null;

        const baseX = (from.x + to.x) / 2;
        const baseY = (from.y + to.y) / 2;
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const len = Math.max(1, Math.hypot(dx, dy));

        return {
          key: `${edge.from}-${edge.to}-label`,
          text: edge.label,
          baseX,
          baseY,
          nx: -dy / len,
          ny: dx / len,
          tx: dx / len,
          ty: dy / len,
          width: Math.max(56, Math.ceil(edge.label.length * 5.7) + 14),
          height: 16,
        };
      })
      .filter(Boolean) as Array<{
      key: string;
      text: string;
      baseX: number;
      baseY: number;
      nx: number;
      ny: number;
      tx: number;
      ty: number;
      width: number;
      height: number;
    }>;

    prepared.sort((a, b) => (a.baseY - b.baseY) || (a.baseX - b.baseX));

    const placed: Array<{ key: string; text: string; x: number; y: number; width: number }> = [];
    for (const label of prepared) {
      let chosen = { x: label.baseX, y: label.baseY - 16 };

      const candidates: Array<{ x: number; y: number }> = [];
      for (let layer = 1; layer <= 7; layer += 1) {
        const normalShift = 14 + layer * 7;
        const tangentShift = (layer - 1) * 7;
        candidates.push({
          x: label.baseX + label.nx * normalShift + label.tx * tangentShift,
          y: label.baseY + label.ny * normalShift + label.ty * tangentShift,
        });
        candidates.push({
          x: label.baseX - label.nx * normalShift + label.tx * tangentShift,
          y: label.baseY - label.ny * normalShift + label.ty * tangentShift,
        });
        candidates.push({
          x: label.baseX + label.nx * normalShift - label.tx * tangentShift,
          y: label.baseY + label.ny * normalShift - label.ty * tangentShift,
        });
        candidates.push({
          x: label.baseX - label.nx * normalShift - label.tx * tangentShift,
          y: label.baseY - label.ny * normalShift - label.ty * tangentShift,
        });
      }

      for (const candidate of candidates) {
        const box: RectBox = {
          x: candidate.x - label.width / 2,
          y: candidate.y - label.height / 2,
          w: label.width,
          h: label.height,
        };
        if (!occupied.some((o) => intersects(box, o))) {
          chosen = candidate;
          occupied.push(box);
          break;
        }
      }

      placed.push({
        key: label.key,
        text: label.text,
        x: chosen.x,
        y: chosen.y,
        width: label.width,
      });
    }

    return placed;
  }, [layout.edges, layout.nodes, byKey]);

  if (!tree.tree) return <div className="tree-empty">Нет данных для отображения</div>;

  return (
    <div className="tree-view dependency-tree">
      <h4>Дерево зависимостей</h4>
      <p className="tree-sentence">"{tree.sentence_text}"</p>
      {tree.root_token && <p className="tree-root">Корень: <strong>{tree.root_token}</strong></p>}
      <div className="tree-svg-container">
        <svg width={layout.width} height={layout.height} style={{ overflow: 'hidden' }}>
          {layout.edges.map((edge) => {
            const from = byKey[edge.from];
            const to = byKey[edge.to];
            if (!from || !to) return null;
            return (
              <g key={`${edge.from}-${edge.to}`}>
                <line
                  x1={from.x}
                  y1={from.y + dependencyNodeRadius(from.node.token, from.node.pos || '')}
                  x2={to.x}
                  y2={to.y - dependencyNodeRadius(to.node.token, to.node.pos || '')}
                  stroke="#616161"
                  strokeWidth="1.5"
                />
              </g>
            );
          })}
          {edgeLabels.map((label) => (
            <g key={label.key}>
              <rect
                x={label.x - label.width / 2}
                y={label.y - 8}
                width={label.width}
                height={16}
                rx={3}
                fill="rgba(255,255,255,0.88)"
                stroke="rgba(120,120,120,0.35)"
              />
              <text x={label.x} y={label.y + 3} textAnchor="middle" fill="#555" fontSize="8.2" fontWeight="600">
                {label.text}
              </text>
            </g>
          ))}
          {layout.nodes.map(({ key, node, x, y }) => {
            const radius = dependencyNodeRadius(node.token, node.pos || '');
            return (
              <g key={key}>
                <circle cx={x} cy={y} r={radius} fill={colorByPos(node.pos)} stroke="#fff" strokeWidth="2" />
                <text x={x} y={y - 2} textAnchor="middle" fill="#fff" fontSize="10" fontWeight="bold">
                  {node.token.length > 12 ? `${node.token.slice(0, 11)}…` : node.token}
                </text>
                <text x={x} y={y + 12} textAnchor="middle" fill="rgba(255,255,255,0.92)" fontSize="8" fontWeight="600">
                  {node.pos || '—'}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <div className="tree-node-meta">
        {tree.flat_representation.map((node) => (
          <span key={node.id} className="tree-node-meta-item">
            <strong>{node.token}</strong>
            <span className="tree-node-meta-pos">{node.pos || '—'}</span>
            {node.pos_name && <span>{node.pos_name}</span>}
            <span>{node.syntax_role_name || node.relation_ru || node.relation}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function ConstituencyTreeView({ tree }: { tree: ConstituencyTree }) {
  const layout = useMemo(() => buildConstituencyLayout(tree.tree), [tree.tree]);
  const byKey = useMemo(() => Object.fromEntries(layout.nodes.map((n) => [n.key, n])), [layout.nodes]);

  if (!tree.tree) return <div className="tree-empty">Нет данных для отображения</div>;

  return (
    <div className="tree-view constituency-tree">
      <h4>Дерево составляющих</h4>
      <p className="tree-sentence">"{tree.sentence_text}"</p>
      {tree.linearized && (
        <p className="tree-linearized">
          <strong>Линейная запись:</strong> {tree.linearized}
        </p>
      )}
      <div className="tree-svg-container">
        <svg width={layout.width} height={layout.height} style={{ overflow: 'visible' }}>
          {layout.edges.map((edge) => {
            const from = byKey[edge.from];
            const to = byKey[edge.to];
            if (!from || !to) return null;
            return (
              <line
                key={`${edge.from}-${edge.to}`}
                x1={from.x}
                y1={from.y + 15}
                x2={to.x}
                y2={to.y - 12}
                stroke="#616161"
                strokeWidth="1.4"
              />
            );
          })}
          {layout.nodes.map(({ key, node, x, y }) => {
            if (typeof node === 'string') {
              return (
                <g key={key}>
                  <rect x={x - 30} y={y - 12} width={60} height={24} rx="5" fill="#ECEFF1" stroke="#90A4AE" />
                  <text x={x} y={y + 4} textAnchor="middle" fill="#37474F" fontSize="9">
                    {node.length > 9 ? `${node.slice(0, 8)}…` : node}
                  </text>
                </g>
              );
            }
            return (
              <g key={key}>
                <rect
                  x={x - 36}
                  y={y - 14}
                  width={72}
                  height={28}
                  rx="6"
                  fill={colorByLabel(node.label)}
                  stroke="#fff"
                  strokeWidth="2"
                />
                <text x={x} y={y + 4} textAnchor="middle" fill="#fff" fontSize="10" fontWeight="bold">
                  {node.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

export default function TreeVisualization({ dependencyTrees = [], constituencyTrees = [] }: TreeVisualizationProps) {
  const [activeTab, setActiveTab] = useState<'dependency' | 'constituency'>('dependency');
  const [selectedSentence, setSelectedSentence] = useState(0);

  if (dependencyTrees.length === 0 && constituencyTrees.length === 0) {
    return <div className="tree-visualization"><p className="no-trees">Деревья ещё не построены</p></div>;
  }

  const depTree = dependencyTrees[selectedSentence];
  const constTree = constituencyTrees[selectedSentence];
  const sentenceCount = Math.max(dependencyTrees.length, constituencyTrees.length);

  return (
    <div className="tree-visualization">
      <div className="tree-tabs">
        <button className={activeTab === 'dependency' ? 'active' : ''} onClick={() => setActiveTab('dependency')}>
          Дерево зависимостей
        </button>
        <button className={activeTab === 'constituency' ? 'active' : ''} onClick={() => setActiveTab('constituency')}>
          Дерево составляющих
        </button>
      </div>

      {sentenceCount > 1 && (
        <div className="tree-sentence-selector">
          <label>Предложение:</label>
          <select value={selectedSentence} onChange={(e) => setSelectedSentence(Number(e.target.value))}>
            {Array.from({ length: sentenceCount }, (_, idx) => (
              <option key={idx} value={idx}>{idx + 1}</option>
            ))}
          </select>
        </div>
      )}

      {activeTab === 'dependency'
        ? (depTree ? <DependencyTreeView tree={depTree} /> : <div className="tree-empty">Нет дерева зависимостей</div>)
        : (constTree ? <ConstituencyTreeView tree={constTree} /> : <div className="tree-empty">Нет дерева составляющих</div>)}
    </div>
  );
}
