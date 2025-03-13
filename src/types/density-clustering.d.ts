declare module 'density-clustering' {
  export class DBSCAN {
    run(dataset: number[][], epsilon: number, minPoints: number): number[][];
  }

  export class KMEANS {
    run(dataset: number[][], k: number, options?: { maxIterations?: number }): {
      clusters: number[][];
      centroids: number[][];
    };
  }

  export class OPTICS {
    run(dataset: number[][], epsilon: number, minPoints: number): number[][];
  }
}
