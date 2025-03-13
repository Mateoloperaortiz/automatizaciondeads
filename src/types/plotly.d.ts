declare module 'plotly.js-dist' {
  export interface Data {
    type?: string;
    x?: Array<number | string>;
    y?: Array<number | string>;
    z?: Array<Array<number>>;
    text?: string | string[];
    mode?: string;
    name?: string;
    marker?: {
      color?: string | string[];
      size?: number | number[];
      symbol?: string | string[];
      line?: {
        color?: string;
        width?: number;
      };
    };
    textposition?: string;
    textfont?: {
      size?: number;
      color?: string;
    };
    hoverinfo?: string;
    [key: string]: unknown;
  }

  export interface Layout {
    title?: string | {
      text: string;
      font?: {
        family?: string;
        size?: number;
        color?: string;
      };
    };
    showlegend?: boolean;
    width?: number;
    height?: number;
    hovermode?: string;
    xaxis?: {
      title?: string | {
        text: string;
      };
      showticklabels?: boolean;
      zeroline?: boolean;
    };
    yaxis?: {
      title?: string | {
        text: string;
      };
      showticklabels?: boolean;
      zeroline?: boolean;
    };
    margin?: {
      l?: number;
      r?: number;
      t?: number;
      b?: number;
      pad?: number;
    };
    [key: string]: unknown;
  }

  export function newPlot(
    graphDiv: HTMLElement | string,
    data: Data[],
    layout?: Partial<Layout>,
    config?: Record<string, unknown>
  ): Promise<Record<string, unknown>>;

  export function purge(graphDiv: HTMLElement | string): void;
}
