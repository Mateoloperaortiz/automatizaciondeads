/**
 * Performance Test Suite
 * Automated tests for application performance using Puppeteer
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Base URL for testing
const BASE_URL = process.env.TEST_URL || 'http://localhost:5000';

// Performance thresholds
const THRESHOLDS = {
  FIRST_CONTENTFUL_PAINT: 1500, // milliseconds
  LARGEST_CONTENTFUL_PAINT: 2500, // milliseconds
  CUMULATIVE_LAYOUT_SHIFT: 0.1, // unitless
  FIRST_INPUT_DELAY: 100, // milliseconds
  TOTAL_BLOCKING_TIME: 200, // milliseconds
  LOAD_TIME: 3000, // milliseconds
  
  // API response times
  API_RESPONSE_TIME: 500, // milliseconds
  
  // Memory usage
  MEMORY_USAGE: 50, // MB
  
  // CPU usage
  CPU_USAGE: 80, // percentage
  
  // FPS (frames per second)
  MIN_FPS: 30, // frames per second
};

// Pages to test
const PAGES = [
  { name: 'Dashboard', path: '/dashboard', expectedElements: ['.metric-card', '.chart-container'] },
  { name: 'Job Openings', path: '/job_openings', expectedElements: ['.table-container'] },
  { name: 'Campaigns', path: '/campaigns', expectedElements: ['.table-container'] },
  { name: 'Analytics', path: '/analytics', expectedElements: ['.chart-container'] },
];

// User interactions to test
const INTERACTIONS = [
  {
    name: 'Dashboard Refresh',
    page: '/dashboard',
    action: async (page) => {
      // Find and click refresh button
      await page.waitForSelector('.card-header .actions button:has(i.fa-sync-alt)', { timeout: 5000 });
      await page.click('.card-header .actions button:has(i.fa-sync-alt)');
      await page.waitForTimeout(1000); // Wait for refresh to complete
    }
  },
  {
    name: 'Table Sorting',
    page: '/campaigns',
    action: async (page) => {
      // Find and click a table header to sort
      await page.waitForSelector('th', { timeout: 5000 });
      await page.click('th:first-child');
      await page.waitForTimeout(500);
      // Click again to reverse sort
      await page.click('th:first-child');
      await page.waitForTimeout(500);
    }
  },
  {
    name: 'Tab Navigation',
    page: '/analytics',
    action: async (page) => {
      // Find and click tab navigation
      await page.waitForSelector('.nav-tabs .nav-link', { timeout: 5000 });
      const tabs = await page.$$('.nav-tabs .nav-link');
      if (tabs.length >= 2) {
        await tabs[1].click();
        await page.waitForTimeout(500);
      }
    }
  },
];

/**
 * Run page load performance tests
 */
async function runPageLoadPerformanceTests() {
  console.log(`Starting page load performance tests against ${BASE_URL}`);
  
  const browser = await puppeteer.launch({
    headless: true,
    defaultViewport: { width: 1920, height: 1080 }
  });
  
  const results = {
    pages: {},
    summary: {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0
    }
  };
  
  try {
    // Test each page
    for (const pageConfig of PAGES) {
      console.log(`\nTesting ${pageConfig.name}...`);
      results.pages[pageConfig.name] = {};
      
      const page = await browser.newPage();
      
      // Enable CPU and memory monitoring
      await page.setCPUThrottlingRate(4); // Simulate slower CPU
      
      // Enable performance metrics collection
      await page.evaluateOnNewDocument(() => {
        window.performance.mark('custom_page_load_start');
        
        // Record long tasks
        const longTaskObserver = new PerformanceObserver((list) => {
          window._longTasks = window._longTasks || [];
          for (const entry of list.getEntries()) {
            window._longTasks.push({
              duration: entry.duration,
              startTime: entry.startTime,
              name: entry.name
            });
          }
        });
        
        try {
          longTaskObserver.observe({ entryTypes: ['longtask'] });
        } catch (e) {
          // Not supported in all browsers
          console.warn('LongTask observer not supported');
        }
        
        // Record FPS
        window._frames = [];
        let lastFrameTime = performance.now();
        
        function recordFrame(timestamp) {
          const frameDuration = timestamp - lastFrameTime;
          lastFrameTime = timestamp;
          
          if (frameDuration > 0) {
            window._frames.push({
              time: timestamp,
              duration: frameDuration,
              fps: 1000 / frameDuration
            });
          }
          
          window.requestAnimationFrame(recordFrame);
        }
        
        window.requestAnimationFrame(recordFrame);
      });
      
      // Collect metrics
      let metrics = {};
      
      // Navigate to the page and wait for network to be idle
      const navigationStart = Date.now();
      const response = await page.goto(`${BASE_URL}${pageConfig.path}`, {
        waitUntil: 'networkidle0'
      });
      const navigationEnd = Date.now();
      
      // Check if page loaded correctly
      if (!response.ok()) {
        console.error(`Error loading ${pageConfig.name}: ${response.status()} ${response.statusText()}`);
        results.pages[pageConfig.name].error = `HTTP ${response.status()}: ${response.statusText()}`;
        continue;
      }
      
      // Check if expected elements are present
      let missingElements = [];
      for (const selector of pageConfig.expectedElements) {
        try {
          await page.waitForSelector(selector, { timeout: 5000 });
        } catch (error) {
          missingElements.push(selector);
        }
      }
      
      if (missingElements.length > 0) {
        console.error(`Missing elements on ${pageConfig.name}:`, missingElements);
        results.pages[pageConfig.name].missingElements = missingElements;
      }
      
      // Extract performance metrics
      metrics = await page.evaluate(() => {
        // Mark custom end time
        performance.mark('custom_page_load_end');
        performance.measure('custom_page_load', 'custom_page_load_start', 'custom_page_load_end');
        
        // Get all performance entries
        const perfEntries = performance.getEntriesByType('navigation')[0];
        const paintEntries = performance.getEntriesByType('paint');
        const resourceEntries = performance.getEntriesByType('resource');
        const customMeasures = performance.getEntriesByName('custom_page_load');
        
        // Calculate paint metrics
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint')?.startTime;
        const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime;
        
        // Calculate load metrics
        const domContentLoaded = perfEntries.domContentLoadedEventEnd - perfEntries.startTime;
        const loadTime = perfEntries.loadEventEnd - perfEntries.startTime;
        const customLoadTime = customMeasures[0]?.duration;
        
        // Calculate resource metrics
        const resourceStats = {
          total: resourceEntries.length,
          totalSize: resourceEntries.reduce((sum, entry) => sum + (entry.transferSize || 0), 0),
          byType: {}
        };
        
        resourceEntries.forEach(entry => {
          const type = getResourceType(entry.name);
          if (!resourceStats.byType[type]) {
            resourceStats.byType[type] = {
              count: 0,
              totalSize: 0
            };
          }
          
          resourceStats.byType[type].count++;
          resourceStats.byType[type].totalSize += entry.transferSize || 0;
        });
        
        // Collect FPS data
        const frames = window._frames || [];
        let fps = 0;
        if (frames.length > 0) {
          const recentFrames = frames.slice(-60); // Last ~1 second of frames
          const totalDuration = recentFrames.reduce((sum, frame) => sum + frame.duration, 0);
          fps = recentFrames.length / (totalDuration / 1000);
        }
        
        // Memory usage if available
        let memory = null;
        if (window.performance.memory) {
          memory = {
            totalJSHeapSize: window.performance.memory.totalJSHeapSize / (1024 * 1024),
            usedJSHeapSize: window.performance.memory.usedJSHeapSize / (1024 * 1024),
            jsHeapSizeLimit: window.performance.memory.jsHeapSizeLimit / (1024 * 1024)
          };
        }
        
        // Long tasks
        const longTasks = window._longTasks || [];
        const totalBlockingTime = longTasks.reduce((sum, task) => sum + task.duration, 0);
        
        // Helper function to determine resource type
        function getResourceType(url) {
          const extension = url.split('.').pop().toLowerCase().split('?')[0];
          
          if (['js'].includes(extension)) return 'script';
          if (['css'].includes(extension)) return 'style';
          if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(extension)) return 'image';
          if (['woff', 'woff2', 'ttf', 'otf', 'eot'].includes(extension)) return 'font';
          if (['json'].includes(extension)) return 'data';
          if (url.includes('/api/')) return 'api';
          
          return 'other';
        }
        
        return {
          firstPaint,
          firstContentfulPaint,
          domContentLoaded,
          loadTime,
          customLoadTime,
          resourceStats,
          fps,
          memory,
          longTasks: {
            count: longTasks.length,
            totalBlockingTime
          }
        };
      });
      
      // Add network timing
      metrics.networkTiming = {
        navigationTime: navigationEnd - navigationStart,
        responseStatus: response.status(),
      };
      
      // Calculate overall score
      const loadTimeScore = metrics.loadTime < THRESHOLDS.LOAD_TIME ? 1 : THRESHOLDS.LOAD_TIME / metrics.loadTime;
      const fcpScore = metrics.firstContentfulPaint < THRESHOLDS.FIRST_CONTENTFUL_PAINT ? 1 : THRESHOLDS.FIRST_CONTENTFUL_PAINT / metrics.firstContentfulPaint;
      const tbtScore = metrics.longTasks.totalBlockingTime < THRESHOLDS.TOTAL_BLOCKING_TIME ? 1 : THRESHOLDS.TOTAL_BLOCKING_TIME / metrics.longTasks.totalBlockingTime;
      const fpsScore = (metrics.fps || 0) > THRESHOLDS.MIN_FPS ? 1 : (metrics.fps || 0) / THRESHOLDS.MIN_FPS;
      
      // Combine scores (weighted)
      const overallScore = (loadTimeScore * 0.3) + (fcpScore * 0.3) + (tbtScore * 0.2) + (fpsScore * 0.2);
      const normalizedScore = Math.round(overallScore * 100);
      
      // Test results
      const testResults = {
        loadTimeTest: {
          name: 'Page Load Time',
          value: metrics.loadTime,
          threshold: THRESHOLDS.LOAD_TIME,
          passed: metrics.loadTime < THRESHOLDS.LOAD_TIME
        },
        fcpTest: {
          name: 'First Contentful Paint',
          value: metrics.firstContentfulPaint,
          threshold: THRESHOLDS.FIRST_CONTENTFUL_PAINT,
          passed: metrics.firstContentfulPaint < THRESHOLDS.FIRST_CONTENTFUL_PAINT
        },
        tbtTest: {
          name: 'Total Blocking Time',
          value: metrics.longTasks.totalBlockingTime,
          threshold: THRESHOLDS.TOTAL_BLOCKING_TIME,
          passed: metrics.longTasks.totalBlockingTime < THRESHOLDS.TOTAL_BLOCKING_TIME
        },
        fpsTest: {
          name: 'Frames Per Second',
          value: metrics.fps,
          threshold: THRESHOLDS.MIN_FPS,
          passed: (metrics.fps || 0) > THRESHOLDS.MIN_FPS
        }
      };
      
      // Update summary
      results.summary.totalTests += Object.keys(testResults).length;
      results.summary.passedTests += Object.values(testResults).filter(test => test.passed).length;
      results.summary.failedTests += Object.values(testResults).filter(test => !test.passed).length;
      
      // Store results
      results.pages[pageConfig.name] = {
        metrics,
        score: normalizedScore,
        tests: testResults,
        missingElements: missingElements.length > 0 ? missingElements : null
      };
      
      // Log results
      console.log(`  Score: ${normalizedScore}/100`);
      console.log(`  Load Time: ${Math.round(metrics.loadTime)}ms (threshold: ${THRESHOLDS.LOAD_TIME}ms) - ${testResults.loadTimeTest.passed ? 'PASS' : 'FAIL'}`);
      console.log(`  First Contentful Paint: ${Math.round(metrics.firstContentfulPaint)}ms (threshold: ${THRESHOLDS.FIRST_CONTENTFUL_PAINT}ms) - ${testResults.fcpTest.passed ? 'PASS' : 'FAIL'}`);
      console.log(`  Total Blocking Time: ${Math.round(metrics.longTasks.totalBlockingTime)}ms (threshold: ${THRESHOLDS.TOTAL_BLOCKING_TIME}ms) - ${testResults.tbtTest.passed ? 'PASS' : 'FAIL'}`);
      console.log(`  FPS: ${Math.round(metrics.fps || 0)} (threshold: ${THRESHOLDS.MIN_FPS}) - ${testResults.fpsTest.passed ? 'PASS' : 'FAIL'}`);
      
      // Close the page
      await page.close();
    }
    
    // Test interactions
    console.log('\nTesting user interactions...');
    results.interactions = {};
    
    for (const interaction of INTERACTIONS) {
      console.log(`\nTesting ${interaction.name}...`);
      results.interactions[interaction.name] = {};
      
      const page = await browser.newPage();
      
      // Navigate to the page
      await page.goto(`${BASE_URL}${interaction.page}`, {
        waitUntil: 'networkidle0'
      });
      
      // Prepare for measurement
      await page.evaluate(() => {
        window.interactionMeasurements = [];
        window.interactionErrors = [];
        
        // Set up measurement
        window.startInteractionMeasurement = () => {
          window.interactionStart = performance.now();
        };
        
        window.endInteractionMeasurement = (name) => {
          const duration = performance.now() - window.interactionStart;
          window.interactionMeasurements.push({
            name,
            duration
          });
          window.interactionStart = null;
        };
        
        // Catch errors during interaction
        window.addEventListener('error', (event) => {
          window.interactionErrors.push({
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
          });
        });
      });
      
      // Start measurement
      await page.evaluate(() => {
        window.startInteractionMeasurement();
      });
      
      try {
        // Perform the interaction
        await interaction.action(page);
        
        // End measurement
        const measurements = await page.evaluate((name) => {
          window.endInteractionMeasurement(name);
          return {
            measurements: window.interactionMeasurements,
            errors: window.interactionErrors
          };
        }, interaction.name);
        
        // Check FPS during interaction
        const fps = await page.evaluate(() => {
          const frames = window._frames || [];
          if (frames.length < 2) return 0;
          
          // Get frames during interaction (assuming last ~2 seconds)
          const recentFrames = frames.slice(-120); 
          const totalDuration = recentFrames.reduce((sum, frame) => sum + frame.duration, 0);
          return recentFrames.length / (totalDuration / 1000);
        });
        
        // Record results
        const interactionTime = measurements.measurements[0]?.duration || 0;
        const passed = interactionTime < THRESHOLDS.API_RESPONSE_TIME && fps > THRESHOLDS.MIN_FPS;
        
        results.interactions[interaction.name] = {
          duration: interactionTime,
          fps,
          errors: measurements.errors,
          passed
        };
        
        // Update summary
        results.summary.totalTests += 1;
        if (passed) {
          results.summary.passedTests += 1;
        } else {
          results.summary.failedTests += 1;
        }
        
        // Log results
        console.log(`  Duration: ${Math.round(interactionTime)}ms (threshold: ${THRESHOLDS.API_RESPONSE_TIME}ms) - ${interactionTime < THRESHOLDS.API_RESPONSE_TIME ? 'PASS' : 'FAIL'}`);
        console.log(`  FPS during interaction: ${Math.round(fps)} (threshold: ${THRESHOLDS.MIN_FPS}) - ${fps > THRESHOLDS.MIN_FPS ? 'PASS' : 'FAIL'}`);
        console.log(`  Errors: ${measurements.errors.length}`);
        
      } catch (error) {
        console.error(`Error during interaction ${interaction.name}:`, error);
        results.interactions[interaction.name] = {
          error: error.message,
          passed: false
        };
        
        // Update summary
        results.summary.totalTests += 1;
        results.summary.failedTests += 1;
      }
      
      // Close the page
      await page.close();
    }
    
  } catch (error) {
    console.error('Error running performance tests:', error);
    results.error = error.message;
  } finally {
    // Close the browser
    await browser.close();
  }
  
  // Calculate overall score
  const overallScore = results.summary.totalTests > 0
    ? Math.round((results.summary.passedTests / results.summary.totalTests) * 100)
    : 0;
  
  results.summary.overallScore = overallScore;
  
  // Generate report
  const report = {
    timestamp: new Date().toISOString(),
    baseUrl: BASE_URL,
    thresholds: THRESHOLDS,
    summary: results.summary,
    pages: results.pages,
    interactions: results.interactions
  };
  
  // Save report to file
  const reportPath = path.join(__dirname, 'reports', `performance_${Date.now()}.json`);
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  
  console.log('\nPerformance testing complete!');
  console.log(`Overall Score: ${overallScore}/100`);
  console.log(`Total Tests: ${results.summary.totalTests}, Passed: ${results.summary.passedTests}, Failed: ${results.summary.failedTests}`);
  console.log(`Report saved to ${reportPath}`);
  
  return report;
}

// If run directly (node performance_test.js)
if (require.main === module) {
  // Check if the app is running
  try {
    execSync(`curl -s ${BASE_URL}`);
  } catch (error) {
    console.error(`ERROR: Application doesn't seem to be running at ${BASE_URL}`);
    console.error('Please start the application before running the tests.');
    process.exit(1);
  }
  
  runPageLoadPerformanceTests().catch(error => {
    console.error('Error running performance tests:', error);
    process.exit(1);
  });
}

module.exports = { runPageLoadPerformanceTests };