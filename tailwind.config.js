module.exports = {
  content: [
    "./templates/**/*.html",

    "./reservas/templates/**/*.html",
    "./static/**/*.js",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {},
  }
  ,
  plugins: [
    require("daisyui"),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
  daisyui: {
    themes: ["light", "dark"],
  }
}
