module.exports = {
  plugins: {
    'tailwindcss': {},
    'autoprefixer': {},
    'postcss-import': {},  // Handle @import rules
    'postcss-flexbugs-fixes': {},  // Fix flexbox bugs
    'postcss-preset-env': {  // Convert modern CSS into something browsers understand
      autoprefixer: {
        flexbox: 'no-2009',
        grid: 'autoplace'
      },
      stage: 3,
      features: {
        'custom-properties': false,
        'nesting-rules': true
      }
    }
  }
}
