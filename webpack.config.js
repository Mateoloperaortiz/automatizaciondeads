const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');

// Determinar si estamos en modo producción
const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
  // Modo de webpack (development o production)
  mode: isProduction ? 'production' : 'development',
  
  // Punto de entrada
  entry: {
    main: './adflux/static/src/js/main.js',
    dashboard: './adflux/static/src/js/dashboard.js',
    campaigns: './adflux/static/src/js/campaigns.js',
    candidates: './adflux/static/src/js/candidates.js',
    jobs: './adflux/static/src/js/jobs.js',
    reports: './adflux/static/src/js/reports.js',
    settings: './adflux/static/src/js/settings.js',
  },
  
  // Salida
  output: {
    path: path.resolve(__dirname, 'adflux/static/dist'),
    filename: isProduction ? 'js/[name].[contenthash].js' : 'js/[name].js',
    publicPath: '/static/dist/',
    chunkFilename: isProduction ? 'js/[name].[contenthash].chunk.js' : 'js/[name].chunk.js',
  },
  
  // Optimización
  optimization: {
    minimize: isProduction,
    minimizer: [
      // Minimizar JavaScript
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: isProduction,
            drop_debugger: isProduction,
          },
          output: {
            comments: false,
          },
        },
        extractComments: false,
      }),
      // Minimizar CSS
      new CssMinimizerPlugin(),
    ],
    // Dividir código en chunks
    splitChunks: {
      chunks: 'all',
      name: false,
      cacheGroups: {
        // Chunk para librerías de terceros
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        // Chunk para código común
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5,
          reuseExistingChunk: true,
          enforce: true,
        },
      },
    },
    // Extraer runtime
    runtimeChunk: 'single',
  },
  
  // Módulos
  module: {
    rules: [
      // JavaScript
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            plugins: [
              '@babel/plugin-proposal-class-properties',
              '@babel/plugin-transform-runtime',
            ],
          },
        },
      },
      // CSS
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
        ],
      },
      // SCSS
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
          'sass-loader',
        ],
      },
      // Imágenes
      {
        test: /\.(png|jpe?g|gif|svg|webp)$/i,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8 * 1024, // 8kb
          },
        },
        generator: {
          filename: 'images/[name].[hash][ext][query]',
        },
      },
      // Fuentes
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name].[hash][ext][query]',
        },
      },
    ],
  },
  
  // Plugins
  plugins: [
    // Limpiar directorio de salida
    new CleanWebpackPlugin(),
    
    // Extraer CSS a archivos separados
    new MiniCssExtractPlugin({
      filename: isProduction ? 'css/[name].[contenthash].css' : 'css/[name].css',
      chunkFilename: isProduction ? 'css/[name].[contenthash].chunk.css' : 'css/[name].chunk.css',
    }),
    
    // Generar manifest.json
    new WebpackManifestPlugin({
      fileName: 'manifest.json',
      publicPath: '/static/dist/',
    }),
    
    // Copiar archivos estáticos
    new CopyWebpackPlugin({
      patterns: [
        {
          from: 'adflux/static/src/images',
          to: 'images',
          globOptions: {
            ignore: ['**/*.DS_Store'],
          },
        },
        {
          from: 'adflux/static/src/favicon',
          to: 'favicon',
        },
      ],
    }),
    
    // Optimizar imágenes
    new ImageMinimizerPlugin({
      minimizer: {
        implementation: ImageMinimizerPlugin.imageminMinify,
        options: {
          plugins: [
            ['gifsicle', { interlaced: true }],
            ['jpegtran', { progressive: true }],
            ['optipng', { optimizationLevel: 5 }],
            ['svgo', {
              plugins: [
                {
                  name: 'preset-default',
                  params: {
                    overrides: {
                      removeViewBox: false,
                      addAttributesToSVGElement: {
                        params: {
                          attributes: [
                            { xmlns: 'http://www.w3.org/2000/svg' },
                          ],
                        },
                      },
                    },
                  },
                },
              ],
            }],
          ],
        },
      },
    }),
  ],
  
  // Configuración de desarrollo
  devtool: isProduction ? false : 'source-map',
  
  // Configuración del servidor de desarrollo
  devServer: {
    static: {
      directory: path.join(__dirname, 'adflux/static/dist'),
    },
    compress: true,
    port: 8080,
    hot: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
  
  // Resolución de módulos
  resolve: {
    extensions: ['.js', '.json', '.css', '.scss'],
    alias: {
      '@': path.resolve(__dirname, 'adflux/static/src'),
    },
  },
  
  // Estadísticas
  stats: {
    colors: true,
    modules: false,
    children: false,
    chunks: false,
    chunkModules: false,
  },
  
  // Caché
  cache: {
    type: 'filesystem',
    buildDependencies: {
      config: [__filename],
    },
  },
};
