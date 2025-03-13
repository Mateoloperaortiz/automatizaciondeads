import { AudienceSegment, SegmentationOptions, SegmentationResult, UserProfile } from './types';
import { SegmentationUtils } from './segmentation-utils';
import { kmeans } from 'ml-kmeans';
import { agnes } from 'ml-hclust';
import * as densityClustering from 'density-clustering';

/**
 * Servicio para la segmentación de audiencias utilizando métodos no supervisados
 */
export class AudienceSegmentationService {
  /**
   * Segmenta una lista de usuarios en grupos utilizando el método especificado
   * @param users Lista de perfiles de usuario para segmentar
   * @param options Opciones de segmentación
   * @returns Resultado de la segmentación
   */
  segmentAudience(users: UserProfile[], options: SegmentationOptions): SegmentationResult {
    console.log(`Segmentando ${users.length} usuarios utilizando método ${options.method}`);
    
    let segments: AudienceSegment[] = [];
    
    // Aplicar el método de segmentación seleccionado
    switch (options.method) {
      case 'kmeans':
        segments = this.applyKMeans(users, options);
        break;
      case 'hierarchical':
        segments = this.applyHierarchical(users, options);
        break;
      case 'dbscan':
        segments = this.applyDBSCAN(users, options);
        break;
      default:
        throw new Error(`Método de segmentación no soportado: ${options.method}`);
    }
    
    // Calcular la calidad de la segmentación
    const qualityScore = this.calculateQualityScore(segments, users);
    
    return {
      segments,
      metadata: {
        totalUsers: users.length,
        segmentationMethod: options.method,
        segmentationDate: new Date(),
        qualityScore
      }
    };
  }
  
  /**
   * Implementación del algoritmo K-means para segmentación
   * @param users Lista de perfiles de usuario
   * @param options Opciones de segmentación
   * @returns Segmentos generados
   */
  private applyKMeans(users: UserProfile[], options: SegmentationOptions): AudienceSegment[] {
    const numberOfClusters = options.numberOfClusters || 5;
    console.log(`Aplicando K-means con ${numberOfClusters} clusters`);
    
    // Convertir usuarios a vectores de características
    const { vectors, featureNames, userIndices } = SegmentationUtils.convertUsersToFeatureVectors(users, options.features as string[]);
    
    if (vectors.length === 0) {
      console.warn('No hay suficientes datos para aplicar K-means');
      return [];
    }
    
    // Aplicar algoritmo K-means
    const kmeansResult = kmeans(vectors, numberOfClusters, {
      seed: 42, // Para reproducibilidad
      initialization: 'kmeans++', // Mejor inicialización que la aleatoria
      maxIterations: 100
    });
    
    // Crear mapa de usuarios por cluster
    const usersByCluster: Record<number, UserProfile[]> = {};
    
    kmeansResult.clusters.forEach((clusterId: number, i: number) => {
      if (!usersByCluster[clusterId]) {
        usersByCluster[clusterId] = [];
      }
      
      const userId = userIndices[i];
      const user = users.find(u => u.id === userId);
      
      if (user) {
        usersByCluster[clusterId].push(user);
      }
    });
    
    // Crear segmentos a partir de los clusters
    const segments: AudienceSegment[] = [];
    
    Object.entries(usersByCluster).forEach(([clusterId, clusterUsers], index) => {
      if (clusterUsers.length === 0) return;
      
      const dominantInterests = this.extractDominantInterests(clusterUsers);
      const primaryInterest = dominantInterests[0] || 'general';
      const segmentId = `kmeans_segment_${Date.now()}_${index}`;
      
      segments.push({
        id: segmentId,
        name: `Segmento K-means ${clusterId}: ${primaryInterest}`,
        description: `Usuarios agrupados por K-means con interés principal en ${primaryInterest}`,
        size: clusterUsers.length,
        users: clusterUsers.map(user => user.id),
        characteristics: {
          dominantDemographics: this.extractDominantDemographics(clusterUsers),
          dominantInterests: dominantInterests,
          engagementLevel: this.calculateEngagementLevel(clusterUsers),
          conversionPotential: this.calculateConversionPotential(clusterUsers),
          bestTimeToTarget: this.calculateBestTimeToTarget(clusterUsers)
        },
        createdAt: new Date(),
        updatedAt: new Date(),
        visualizationData: SegmentationUtils.generateVisualizationConfig(
          vectors,
          kmeansResult.clusters,
          featureNames
        )
      });
    });
    
    return segments;
  }
  
  /**
   * Implementación del algoritmo Hierarchical Clustering para segmentación
   * @param users Lista de perfiles de usuario
   * @param options Opciones de segmentación
   * @returns Segmentos generados
   */
  private applyHierarchical(users: UserProfile[], options: SegmentationOptions): AudienceSegment[] {
    const numberOfClusters = options.numberOfClusters || 5;
    console.log(`Aplicando Hierarchical Clustering para generar ${numberOfClusters} clusters`);
    
    // Convertir usuarios a vectores de características
    const { vectors, featureNames, userIndices } = SegmentationUtils.convertUsersToFeatureVectors(users, options.features as string[]);
    
    if (vectors.length === 0) {
      console.warn('No hay suficientes datos para aplicar Hierarchical Clustering');
      return [];
    }
    
    // Calcular matriz de distancias
    const distanceMatrix: number[][] = [];
    for (let i = 0; i < vectors.length; i++) {
      const row: number[] = [];
      for (let j = 0; j < vectors.length; j++) {
        row.push(SegmentationUtils.euclideanDistance(vectors[i], vectors[j]));
      }
      distanceMatrix.push(row);
    }
    
    // Aplicar algoritmo de clustering jerárquico (AGNES - Agglomerative Nesting)
    const agnesResult = agnes(distanceMatrix, {
      method: 'ward' // Método de vinculación
    });
    
    // Obtener clusters cortando el dendrograma al nivel que da el número de clusters deseado
    const clusters = agnesResult.cut(numberOfClusters);
    // Convertir a tipo adecuado para TypeScript
    const clusterArray: number[][] = [];    
    for (let i = 0; i < clusters.length; i++) {
      if (clusters[i] && Array.isArray(clusters[i])) {
        clusterArray.push(clusters[i] as unknown as number[]);
      }
    }
    
    // Crear mapa de usuarios por cluster
    const usersByCluster: Record<number, UserProfile[]> = {};
    
    // Usar el array de clusters correctamente tipado
    clusterArray.forEach((clusterPoints: number[], clusterId: number) => {
      if (!usersByCluster[clusterId]) {
        usersByCluster[clusterId] = [];
      }
      
      // Procesar cada punto en el cluster
      clusterPoints.forEach((pointIndex: number) => {
        const userId = userIndices[pointIndex];
        const user = users.find(u => u.id === userId);
        
        if (user) {
          usersByCluster[clusterId].push(user);
        }
      });
    });
    
    // Crear segmentos a partir de los clusters
    const segments: AudienceSegment[] = [];
    
    Object.entries(usersByCluster).forEach(([clusterId, clusterUsers], index) => {
      if (clusterUsers.length === 0) return;
      
      // Extraer características dominantes del cluster
      const dominantDemographics = this.extractDominantDemographics(clusterUsers);
      const dominantLocation = dominantDemographics.location || 'desconocida';
      const dominantInterests = this.extractDominantInterests(clusterUsers);
      
      const segmentId = `hc_segment_${Date.now()}_${index}`;
      
      segments.push({
        id: segmentId,
        name: `Segmento Jerárquico ${clusterId}: ${dominantLocation}`,
        description: `Usuarios agrupados jerárquicamente con ubicación principal en ${dominantLocation}`,
        size: clusterUsers.length,
        users: clusterUsers.map(user => user.id),
        characteristics: {
          dominantDemographics,
          dominantInterests,
          engagementLevel: this.calculateEngagementLevel(clusterUsers),
          conversionPotential: this.calculateConversionPotential(clusterUsers),
          bestTimeToTarget: this.calculateBestTimeToTarget(clusterUsers)
        },
        createdAt: new Date(),
        updatedAt: new Date(),
        visualizationData: SegmentationUtils.generateVisualizationConfig(
          vectors,
          clusterArray.map((_, i) => i), // Convert to cluster assignments array
          featureNames
        )
      });
    });
    
    return segments;
  }
  
  /**
   * Implementación del algoritmo DBSCAN para segmentación
   * @param users Lista de perfiles de usuario
   * @param options Opciones de segmentación
   * @returns Segmentos generados
   */
  private applyDBSCAN(users: UserProfile[], options: SegmentationOptions): AudienceSegment[] {
    const minPoints = options.minPoints || 5;
    const epsilon = options.epsilon || 0.5;
    console.log(`Aplicando DBSCAN con minPoints=${minPoints} y epsilon=${epsilon}`);
    
    // Convertir usuarios a vectores de características
    const { vectors, featureNames, userIndices } = SegmentationUtils.convertUsersToFeatureVectors(users, options.features as string[]);
    
    if (vectors.length === 0) {
      console.warn('No hay suficientes datos para aplicar DBSCAN');
      return [];
    }
    
    // Aplicar algoritmo DBSCAN
    const dbscan = new densityClustering.DBSCAN();
    const clusters = dbscan.run(vectors, epsilon, minPoints);
    
    // Crear mapa de usuarios por cluster
    const usersByCluster: Record<number, UserProfile[]> = {};
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const noise: UserProfile[] = [];
    
    // Inicializar cluster -1 para puntos de ruido
    usersByCluster[-1] = [];
    
    // Asignar usuarios a clusters
    clusters.forEach((clusterPoints: number[], clusterId: number) => {
      usersByCluster[clusterId] = [];
      
      clusterPoints.forEach((pointIndex: number) => {
        const userId = userIndices[pointIndex];
        const user = users.find(u => u.id === userId);
        
        if (user) {
          usersByCluster[clusterId].push(user);
        }
      });
    });
    
    // Identificar puntos de ruido (no asignados a ningún cluster)
    const assignedIndices = new Set<number>();
    clusters.forEach((cluster: number[]) => {
      cluster.forEach((index: number) => assignedIndices.add(index));
    });
    
    for (let i = 0; i < vectors.length; i++) {
      if (!assignedIndices.has(i)) {
        const userId = userIndices[i];
        const user = users.find(u => u.id === userId);
        
        if (user) {
          usersByCluster[-1].push(user);
        }
      }
    }
    
    // Crear segmentos a partir de los clusters
    const segments: AudienceSegment[] = [];
    
    // Crear un array plano de asignaciones de cluster para visualización
    const clusterAssignments: number[] = new Array(vectors.length).fill(-1);
    clusters.forEach((clusterPoints: number[], clusterId: number) => {
      clusterPoints.forEach((pointIndex: number) => {
        clusterAssignments[pointIndex] = clusterId;
      });
    });
    
    // Eliminar variables no utilizadas para evitar advertencias
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const _noise: UserProfile[] = [];
    
    Object.entries(usersByCluster).forEach(([clusterIdStr, clusterUsers]) => {
      if (clusterUsers.length === 0) return;
      
      const clusterId = parseInt(clusterIdStr);
      
      // Los puntos de ruido (clusterId = -1) se manejan de manera especial
      if (clusterId === -1 && clusterUsers.length > 0) {
        segments.push({
          id: `dbscan_noise_${Date.now()}`,
          name: 'Segmento de Outliers',
          description: 'Usuarios que no encajan en ningún patrón de comportamiento definido',
          size: clusterUsers.length,
          users: clusterUsers.map(user => user.id),
          characteristics: {
            dominantDemographics: this.extractDominantDemographics(clusterUsers),
            dominantInterests: this.extractDominantInterests(clusterUsers),
            engagementLevel: this.calculateEngagementLevel(clusterUsers),
            conversionPotential: this.calculateConversionPotential(clusterUsers),
            bestTimeToTarget: this.calculateBestTimeToTarget(clusterUsers)
          },
          createdAt: new Date(),
          updatedAt: new Date(),
          visualizationData: SegmentationUtils.generateVisualizationConfig(
            vectors,
            clusterAssignments,
            featureNames
          )
        });
        return;
      }
      
      // Determinar el nivel de engagement predominante en el cluster
      const engagementLevel = this.calculateEngagementLevel(clusterUsers);
      const levelName = engagementLevel.charAt(0).toUpperCase() + engagementLevel.slice(1);
      
      const segmentId = `dbscan_segment_${Date.now()}_${clusterId}`;
      
      segments.push({
        id: segmentId,
        name: `Segmento DBSCAN ${clusterId}: Engagement ${levelName}`,
        description: `Usuarios agrupados por patrones de comportamiento con nivel de engagement ${engagementLevel}`,
        size: clusterUsers.length,
        users: clusterUsers.map(user => user.id),
        characteristics: {
          dominantDemographics: this.extractDominantDemographics(clusterUsers),
          dominantInterests: this.extractDominantInterests(clusterUsers),
          engagementLevel: engagementLevel as 'low' | 'medium' | 'high',
          conversionPotential: this.calculateConversionPotential(clusterUsers),
          bestTimeToTarget: this.calculateBestTimeToTarget(clusterUsers)
        },
        createdAt: new Date(),
        updatedAt: new Date(),
        visualizationData: SegmentationUtils.generateVisualizationConfig(
          vectors,
          clusterAssignments,
          featureNames
        )
      });
    });
    
    return segments;
  }
  
  /**
   * Agrupa usuarios por sus intereses principales
   */
  private groupUsersByInterests(users: UserProfile[]): Record<string, UserProfile[]> {
    const groups: Record<string, UserProfile[]> = {};
    
    users.forEach(user => {
      if (user.behavior.interests.length === 0) return;
      
      // Usar el primer interés como categoría principal para simplificar
      const primaryInterest = user.behavior.interests[0];
      
      if (!groups[primaryInterest]) {
        groups[primaryInterest] = [];
      }
      
      groups[primaryInterest].push(user);
    });
    
    return groups;
  }
  
  /**
   * Agrupa usuarios por ubicación
   */
  private groupUsersByLocation(users: UserProfile[]): Record<string, UserProfile[]> {
    const groups: Record<string, UserProfile[]> = {};
    
    users.forEach(user => {
      if (!user.demographics.location) return;
      
      const location = user.demographics.location;
      
      if (!groups[location]) {
        groups[location] = [];
      }
      
      groups[location].push(user);
    });
    
    return groups;
  }
  
  /**
   * Extrae las características demográficas dominantes de un grupo de usuarios
   */
  private extractDominantDemographics(users: UserProfile[]): Partial<UserProfile['demographics']> {
    if (users.length === 0) return {};
    
    // En una implementación real, calcularíamos los valores más frecuentes
    // Para esta simulación, usaremos el primer usuario como muestra
    
    const demographics: Partial<UserProfile['demographics']> = {};
    
    // Contar ocurrencias de cada valor para cada característica demográfica
    const genderCount: Record<string, number> = {};
    const educationCount: Record<string, number> = {};
    const industryCount: Record<string, number> = {};
    
    let totalAge = 0;
    let ageCount = 0;
    
    users.forEach(user => {
      if (user.demographics.gender) {
        genderCount[user.demographics.gender] = (genderCount[user.demographics.gender] || 0) + 1;
      }
      
      if (user.demographics.educationLevel) {
        educationCount[user.demographics.educationLevel] = (educationCount[user.demographics.educationLevel] || 0) + 1;
      }
      
      if (user.demographics.industry) {
        industryCount[user.demographics.industry] = (industryCount[user.demographics.industry] || 0) + 1;
      }
      
      if (user.demographics.age) {
        totalAge += user.demographics.age;
        ageCount++;
      }
    });
    
    // Encontrar los valores más frecuentes
    if (Object.keys(genderCount).length > 0) {
      demographics.gender = Object.entries(genderCount)
        .sort((a, b) => b[1] - a[1])[0][0] as 'male' | 'female' | 'other';
    }
    
    if (Object.keys(educationCount).length > 0) {
      demographics.educationLevel = Object.entries(educationCount)
        .sort((a, b) => b[1] - a[1])[0][0];
    }
    
    if (Object.keys(industryCount).length > 0) {
      demographics.industry = Object.entries(industryCount)
        .sort((a, b) => b[1] - a[1])[0][0];
    }
    
    if (ageCount > 0) {
      demographics.age = Math.round(totalAge / ageCount);
    }
    
    return demographics;
  }
  
  /**
   * Extrae los intereses secundarios más comunes de un grupo de usuarios, excluyendo el interés principal
   */
  private extractSecondaryInterests(users: UserProfile[], primaryInterest: string): string[] {
    const interestCount: Record<string, number> = {};
    
    users.forEach(user => {
      user.behavior.interests.forEach(interest => {
        if (interest !== primaryInterest) {
          interestCount[interest] = (interestCount[interest] || 0) + 1;
        }
      });
    });
    
    return Object.entries(interestCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(entry => entry[0]);
  }
  
  /**
   * Extrae los intereses dominantes de un grupo de usuarios
   */
  private extractDominantInterests(users: UserProfile[]): string[] {
    const interestCount: Record<string, number> = {};
    
    users.forEach(user => {
      user.behavior.interests.forEach(interest => {
        interestCount[interest] = (interestCount[interest] || 0) + 1;
      });
    });
    
    return Object.entries(interestCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(entry => entry[0]);
  }
  
  /**
   * Calcula el nivel de engagement promedio de un grupo de usuarios
   */
  private calculateEngagementLevel(users: UserProfile[]): 'low' | 'medium' | 'high' {
    if (users.length === 0) return 'medium';
    
    let totalEngagementScore = 0;
    
    users.forEach(user => {
      let userScore = 0;
      let factors = 0;
      
      if (user.engagement.clickRate !== undefined) {
        userScore += user.engagement.clickRate * 10; // Normalizar a escala 0-10
        factors++;
      }
      
      if (user.engagement.conversionRate !== undefined) {
        userScore += user.engagement.conversionRate * 20; // Dar más peso a las conversiones
        factors++;
      }
      
      if (user.engagement.timeOnSite !== undefined) {
        userScore += Math.min(user.engagement.timeOnSite / 60, 10); // Normalizar minutos a escala 0-10
        factors++;
      }
      
      if (user.engagement.pageViewsPerSession !== undefined) {
        userScore += Math.min(user.engagement.pageViewsPerSession, 10); // Limitar a 10
        factors++;
      }
      
      if (user.engagement.returnRate !== undefined) {
        userScore += user.engagement.returnRate * 10; // Normalizar a escala 0-10
        factors++;
      }
      
      if (user.engagement.socialInteractions !== undefined) {
        userScore += Math.min(user.engagement.socialInteractions, 10); // Limitar a 10
        factors++;
      }
      
      totalEngagementScore += factors > 0 ? userScore / factors : 5; // Valor por defecto: 5 (medio)
    });
    
    const averageEngagementScore = totalEngagementScore / users.length;
    
    if (averageEngagementScore < 3.5) return 'low';
    if (averageEngagementScore > 7) return 'high';
    return 'medium';
  }
  
  /**
   * Calcula el potencial de conversión de un grupo de usuarios
   */
  private calculateConversionPotential(users: UserProfile[]): 'low' | 'medium' | 'high' {
    if (users.length === 0) return 'medium';
    
    let totalConversionScore = 0;
    let usersWithData = 0;
    
    users.forEach(user => {
      if (user.engagement.conversionRate !== undefined) {
        totalConversionScore += user.engagement.conversionRate;
        usersWithData++;
      }
    });
    
    if (usersWithData === 0) return 'medium';
    
    const averageConversionRate = totalConversionScore / usersWithData;
    
    if (averageConversionRate < 0.02) return 'low';
    if (averageConversionRate > 0.05) return 'high';
    return 'medium';
  }
  
  /**
   * Calcula el mejor momento para dirigirse a un grupo de usuarios
   */
  private calculateBestTimeToTarget(users: UserProfile[]): {
    hours: number[];
    days: ('monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday')[];
  } | undefined {
    const hourCounts: Record<number, number> = {};
    const dayCounts: Record<string, number> = {};
    
    let usersWithHourData = 0;
    let usersWithDayData = 0;
    
    users.forEach(user => {
      if (user.behavior.activeHours && user.behavior.activeHours.length > 0) {
        user.behavior.activeHours.forEach(hour => {
          hourCounts[hour] = (hourCounts[hour] || 0) + 1;
        });
        usersWithHourData++;
      }
      
      if (user.behavior.activeDays && user.behavior.activeDays.length > 0) {
        user.behavior.activeDays.forEach(day => {
          dayCounts[day] = (dayCounts[day] || 0) + 1;
        });
        usersWithDayData++;
      }
    });
    
    if (usersWithHourData === 0 || usersWithDayData === 0) return undefined;
    
    // Encontrar las horas más activas (top 3)
    const topHours = Object.entries(hourCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(entry => parseInt(entry[0]));
    
    // Encontrar los días más activos (top 3)
    const topDays = Object.entries(dayCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(entry => entry[0]) as ('monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday')[];
    
    return {
      hours: topHours,
      days: topDays
    };
  }
  
  /**
   * Calcula la calidad de la segmentación
   * @param segments Segmentos generados
   * @param allUsers Todos los usuarios originales
   * @returns Puntuación de calidad (0-1)
   */
  private calculateQualityScore(segments: AudienceSegment[], allUsers: UserProfile[]): number {
    if (segments.length === 0) return 0;
    
    // En una implementación real, calcularíamos métricas como:
    // - Cohesión intra-cluster (qué tan similares son los usuarios dentro de un segmento)
    // - Separación inter-cluster (qué tan diferentes son los segmentos entre sí)
    // - Cobertura (qué porcentaje de usuarios están asignados a un segmento)
    
    // Para esta simulación, usaremos una métrica simple basada en la cobertura
    const usersInSegments = new Set<string>();
    
    segments.forEach(segment => {
      segment.users.forEach(userId => {
        usersInSegments.add(userId);
      });
    });
    
    const coverage = usersInSegments.size / allUsers.length;
    
    // Simular una puntuación de calidad que combina cobertura con otros factores
    const segmentSizeVariance = this.calculateSegmentSizeVariance(segments);
    const qualityScore = coverage * (1 - segmentSizeVariance);
    
    return Math.min(Math.max(qualityScore, 0), 1); // Asegurar que esté en el rango 0-1
  }
  
  /**
   * Calcula la varianza en el tamaño de los segmentos (0-1)
   * Un valor más bajo indica tamaños más equilibrados
   */
  private calculateSegmentSizeVariance(segments: AudienceSegment[]): number {
    if (segments.length <= 1) return 0;
    
    const sizes = segments.map(segment => segment.size);
    const meanSize = sizes.reduce((sum, size) => sum + size, 0) / sizes.length;
    
    const variance = sizes.reduce((sum, size) => sum + Math.pow(size - meanSize, 2), 0) / sizes.length;
    const maxPossibleVariance = Math.pow(meanSize * segments.length, 2) / segments.length;
    
    return Math.min(variance / maxPossibleVariance, 1);
  }
}
