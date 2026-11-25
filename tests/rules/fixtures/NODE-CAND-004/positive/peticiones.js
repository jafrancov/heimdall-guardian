const axios = require("axios");
async function traer(url, host) {
  await fetch(url);
  await axios.get(url);
  await axios.post("https://" + host + "/datos", {});
  http.get(url, () => {});
}
