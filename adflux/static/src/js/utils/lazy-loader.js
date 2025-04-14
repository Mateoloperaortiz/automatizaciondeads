/**
 * Utilidad para cargar recursos de manera perezosa (lazy loading).
 * 
 * Esta utilidad proporciona funciones para cargar JavaScript, CSS e imágenes
 * solo cuando son necesarios, mejorando el rendimiento de carga inicial.
 */

/**
 * Carga un script JavaScript de manera perezosa.
 * 
 * @param {string} src - URL del script a cargar
 * @param {Object} [options] - Opciones adicionales
 * @param {boolean} [options.async=true] - Si el script debe cargarse de manera asíncrona
 * @param {boolean} [options.defer=true] - Si el script debe diferirse
 * @param {string} [options.type='text/javascript'] - Tipo MIME del script
 * @param {Function} [options.callback] - Función a ejecutar cuando el script se carga
 * @returns {Promise<HTMLScriptElement>} - Promesa que se resuelve cuando el script se carga
 */
export function loadScript(src, options = {}) {
  const {
    async = true,
    defer = true,
    type = 'text/javascript',
    callback = null
  } = options;
  
  return new Promise((resolve, reject) => {
    // Verificar si el script ya está cargado
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    
    // Crear elemento script
    const script = document.createElement('script');
    script.src = src;
    script.type = type;
    script.async = async;
    script.defer = defer;
    
    // Manejar eventos de carga
    script.onload = () => {
      if (callback) {
        callback();
      }
      resolve(script);
    };
    
    script.onerror = (error) => {
      reject(new Error(`Error al cargar script: ${src}`));
    };
    
    // Añadir script al documento
    document.head.appendChild(script);
  });
}

/**
 * Carga un archivo CSS de manera perezosa.
 * 
 * @param {string} href - URL del archivo CSS a cargar
 * @param {Object} [options] - Opciones adicionales
 * @param {string} [options.media='all'] - Atributo media del CSS
 * @param {Function} [options.callback] - Función a ejecutar cuando el CSS se carga
 * @returns {Promise<HTMLLinkElement>} - Promesa que se resuelve cuando el CSS se carga
 */
export function loadCSS(href, options = {}) {
  const {
    media = 'all',
    callback = null
  } = options;
  
  return new Promise((resolve, reject) => {
    // Verificar si el CSS ya está cargado
    if (document.querySelector(`link[href="${href}"]`)) {
      resolve();
      return;
    }
    
    // Crear elemento link
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.media = media;
    
    // Manejar eventos de carga
    link.onload = () => {
      if (callback) {
        callback();
      }
      resolve(link);
    };
    
    link.onerror = (error) => {
      reject(new Error(`Error al cargar CSS: ${href}`));
    };
    
    // Añadir link al documento
    document.head.appendChild(link);
  });
}

/**
 * Carga una imagen de manera perezosa.
 * 
 * @param {string} src - URL de la imagen a cargar
 * @param {Object} [options] - Opciones adicionales
 * @param {Function} [options.callback] - Función a ejecutar cuando la imagen se carga
 * @returns {Promise<HTMLImageElement>} - Promesa que se resuelve cuando la imagen se carga
 */
export function loadImage(src, options = {}) {
  const {
    callback = null
  } = options;
  
  return new Promise((resolve, reject) => {
    const img = new Image();
    
    // Manejar eventos de carga
    img.onload = () => {
      if (callback) {
        callback(img);
      }
      resolve(img);
    };
    
    img.onerror = (error) => {
      reject(new Error(`Error al cargar imagen: ${src}`));
    };
    
    // Iniciar carga
    img.src = src;
  });
}

/**
 * Carga un módulo JavaScript de manera perezosa utilizando import dinámico.
 * 
 * @param {string} modulePath - Ruta del módulo a cargar
 * @returns {Promise<any>} - Promesa que se resuelve con el módulo cargado
 */
export function loadModule(modulePath) {
  return import(/* webpackChunkName: "[request]" */ `${modulePath}`);
}

/**
 * Configura la carga perezosa de imágenes utilizando Intersection Observer.
 * 
 * @param {string} [selector='img[data-src]'] - Selector para las imágenes a cargar perezosamente
 * @param {Object} [options] - Opciones para el Intersection Observer
 * @param {string} [options.rootMargin='50px 0px'] - Margen para el root
 * @param {number} [options.threshold=0.1] - Umbral de intersección
 */
export function setupLazyImages(selector = 'img[data-src]', options = {}) {
  const {
    rootMargin = '50px 0px',
    threshold = 0.1
  } = options;
  
  // Verificar soporte para Intersection Observer
  if (!('IntersectionObserver' in window)) {
    // Fallback para navegadores que no soportan Intersection Observer
    const images = document.querySelectorAll(selector);
    images.forEach(img => {
      if (img.dataset.src) {
        img.src = img.dataset.src;
        delete img.dataset.src;
      }
    });
    return;
  }
  
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          delete img.dataset.src;
          
          // Dejar de observar la imagen una vez cargada
          observer.unobserve(img);
        }
      }
    });
  }, {
    rootMargin,
    threshold
  });
  
  // Observar todas las imágenes con data-src
  const images = document.querySelectorAll(selector);
  images.forEach(img => {
    observer.observe(img);
  });
}

/**
 * Configura la carga perezosa de iframes utilizando Intersection Observer.
 * 
 * @param {string} [selector='iframe[data-src]'] - Selector para los iframes a cargar perezosamente
 * @param {Object} [options] - Opciones para el Intersection Observer
 * @param {string} [options.rootMargin='50px 0px'] - Margen para el root
 * @param {number} [options.threshold=0.1] - Umbral de intersección
 */
export function setupLazyIframes(selector = 'iframe[data-src]', options = {}) {
  const {
    rootMargin = '50px 0px',
    threshold = 0.1
  } = options;
  
  // Verificar soporte para Intersection Observer
  if (!('IntersectionObserver' in window)) {
    // Fallback para navegadores que no soportan Intersection Observer
    const iframes = document.querySelectorAll(selector);
    iframes.forEach(iframe => {
      if (iframe.dataset.src) {
        iframe.src = iframe.dataset.src;
        delete iframe.dataset.src;
      }
    });
    return;
  }
  
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const iframe = entry.target;
        if (iframe.dataset.src) {
          iframe.src = iframe.dataset.src;
          delete iframe.dataset.src;
          
          // Dejar de observar el iframe una vez cargado
          observer.unobserve(iframe);
        }
      }
    });
  }, {
    rootMargin,
    threshold
  });
  
  // Observar todos los iframes con data-src
  const iframes = document.querySelectorAll(selector);
  iframes.forEach(iframe => {
    observer.observe(iframe);
  });
}

/**
 * Inicializa todas las funcionalidades de carga perezosa.
 */
export function initLazyLoading() {
  // Configurar carga perezosa de imágenes
  setupLazyImages();
  
  // Configurar carga perezosa de iframes
  setupLazyIframes();
  
  // Configurar carga perezosa de componentes
  setupLazyComponents();
}

/**
 * Configura la carga perezosa de componentes utilizando Intersection Observer.
 * 
 * @param {string} [selector='[data-lazy-component]'] - Selector para los componentes a cargar perezosamente
 * @param {Object} [options] - Opciones para el Intersection Observer
 * @param {string} [options.rootMargin='100px 0px'] - Margen para el root
 * @param {number} [options.threshold=0.1] - Umbral de intersección
 */
export function setupLazyComponents(selector = '[data-lazy-component]', options = {}) {
  const {
    rootMargin = '100px 0px',
    threshold = 0.1
  } = options;
  
  // Verificar soporte para Intersection Observer
  if (!('IntersectionObserver' in window)) {
    // Fallback para navegadores que no soportan Intersection Observer
    const components = document.querySelectorAll(selector);
    components.forEach(component => {
      if (component.dataset.lazyComponent) {
        loadComponent(component);
      }
    });
    return;
  }
  
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const component = entry.target;
        if (component.dataset.lazyComponent) {
          loadComponent(component);
          
          // Dejar de observar el componente una vez cargado
          observer.unobserve(component);
        }
      }
    });
  }, {
    rootMargin,
    threshold
  });
  
  // Observar todos los componentes con data-lazy-component
  const components = document.querySelectorAll(selector);
  components.forEach(component => {
    observer.observe(component);
  });
}

/**
 * Carga un componente perezoso.
 * 
 * @param {HTMLElement} component - Elemento del componente a cargar
 */
function loadComponent(component) {
  const componentName = component.dataset.lazyComponent;
  const componentPath = component.dataset.lazyPath || `../components/${componentName}`;
  
  // Cargar módulo del componente
  loadModule(componentPath)
    .then(module => {
      if (typeof module.default === 'function') {
        // Inicializar componente
        module.default(component);
      } else if (typeof module.init === 'function') {
        // Inicializar componente
        module.init(component);
      } else {
        console.warn(`El componente ${componentName} no tiene una función default o init`);
      }
    })
    .catch(error => {
      console.error(`Error al cargar el componente ${componentName}:`, error);
    });
}
