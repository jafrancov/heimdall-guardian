const axios = require("axios");
async function traer(id) {
  await fetch("https://api.example.com/estado");
  await axios.get("https://api.example.com/datos");
  await axios.post("https://api.example.com/eventos", { id });
}
