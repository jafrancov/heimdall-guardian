function ir(app) {
  app.get("/a", (req, res) => res.redirect("/inicio"));
  app.get("/b", (req, res) => res.redirect(`/panel`));
}
