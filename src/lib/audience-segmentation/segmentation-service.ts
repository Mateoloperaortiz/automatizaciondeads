import { AudienceSegment, SegmentationOptions, SegmentationResult, UserProfile } from './types';

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
    
    // En una implementación real, aquí iría el algoritmo K-means
    // Para esta simulación, crearemos segmentos aleatorios
    
    const segments: AudienceSegment[] = [];
    
    // Crear segmentos basados en intereses principales
    const interestGroups = this.groupUsersByInterests(users);
    
    // Convertir los grupos de intereses en segmentos formales
    Object.entries(interestGroups).slice(0, numberOfClusters).forEach(([interest, groupUsers], index) => {
      const segmentId = `segment_${Date.now()}_${index}`;
      
      segments.push({
        id: segmentId,
        name: `Segmento de ${interest}`,
        description: `Usuarios interesados en ${interest}`,
        size: groupUsers.length,
        users: groupUsers.map(user => user.id),
        characteristics: {
          dominantDemographics: this.extractDominantDemographics(groupUsers),
          dominantInterests: [interest, ...this.extractSecondaryInterests(groupUsers, interest)],
          engagementLevel: this.calculateEngagementLevel(groupUsers),
          conversionPotential: this.calculateConversionPotential(groupUsers),
          bestTimeToTarget: this.calculateBestTimeToTarget(groupUsers)
        },
        createdAt: new Date(),
        updatedAt: new Date()
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
    const minSimilarity = options.minSimilarity || 0.7;
    console.log(`Aplicando Hierarchical Clustering con similaridad mínima ${minSimilarity}`);
    
    // En una implementación real, aquí iría el algoritmo de clustering jerárquico
    // Para esta simulación, crearemos segmentos basados en demografía
    
    const segments: AudienceSegment[] = [];
    
    // Agrupar por ubicación como ejemplo de clustering jerárquico
    const locationGroups = this.groupUsersByLocation(users);
    
    // Convertir los grupos de ubicación en segmentos formales
    Object.entries(locationGroups).forEach(([location, groupUsers], index) => {
      const segmentId = `segment_${Date.now()}_${index}`;
      
      segments.push({
        id: segmentId,
        name: `Segmento de ${location}`,
        description: `Usuarios ubicados en ${location}`,
        size: groupUsers.length,
        users: groupUsers.map(user => user.id),
        characteristics: {
          dominantDemographics: { 
            ...this.extractDominantDemographics(groupUsers),
            location 
          },
          dominantInterests: this.extractDominantInterests(groupUsers),
          engagementLevel: this.calculateEngagementLevel(groupUsers),
          conversionPotential: this.calculateConversionPotential(groupUsers),
          bestTimeToTarget: this.calculateBestTimeToTarget(groupUsers)
        },
        createdAt: new Date(),
        updatedAt: new Date()
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
    
    // En una implementación real, aquí iría el algoritmo DBSCAN
    // Para esta simulación, crearemos segmentos basados en nivel de engagement
    
    const segments: AudienceSegment[] = [];
    
    // Dividir usuarios en grupos de engagement (bajo, medio, alto)
    const engagementLevels: Record<string, UserProfile[]> = {
      low: [],
      medium: [],
      high: []
    };
    
    users.forEach(user => {
      const level = this.calculateEngagementLevel([user]);
      engagementLevels[level].push(user);
    });
    
    // Convertir los niveles de engagement en segmentos formales
    Object.entries(engagementLevels).forEach(([level, groupUsers], index) => {
      if (groupUsers.length < minPoints) return; // Simular el concepto de "ruido" en DBSCAN
      
      const segmentId = `segment_${Date.now()}_${index}`;
      const levelName = level.charAt(0).toUpperCase() + level.slice(1);
      
      segments.push({
        id: segmentId,
        name: `Segmento de Engagement ${levelName}`,
        description: `Usuarios con nivel de engagement ${level}`,
        size: groupUsers.length,
        users: groupUsers.map(user => user.id),
        characteristics: {
          dominantDemographics: this.extractDominantDemographics(groupUsers),
          dominantInterests: this.extractDominantInterests(groupUsers),
          engagementLevel: level as 'low' | 'medium' | 'high',
          conversionPotential: this.calculateConversionPotential(groupUsers),
          bestTimeToTarget: this.calculateBestTimeToTarget(groupUsers)
        },
        createdAt: new Date(),
        updatedAt: new Date()
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
